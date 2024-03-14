import ticketpy.model
import time
from collections import namedtuple
from datetime import datetime

@staticmethod
def __error(response):
    """HTTP status code 400, or something with 'errors' object"""
    rj = response.json()
    error = namedtuple('error', ['code', 'detail', 'href'])
    def get_part(err, *parts):
            try:
                for part in parts:
                    err = err[part]
            except KeyError:
                pass
            
            return err

    errors = [
        error(get_part(err, 'code'), get_part(err, 'detail'), get_part(err, '_links', 'self', 'href'))
        for err in rj['errors']
    ]
    ticketpy.client.log.error('URL: {}\nErrors: {}'.format(response.url, errors))
    raise ticketpy.client.ApiException(response.status_code, errors, response.url)

ticketpy.client.ApiClient._ApiClient__error = __error

rate = 5 # per period
period = 1.2 # seconds
last_query_time = time.time() - period
interval = period / rate

def __get(self, **kwargs):
    """Sends final request to ``ApiClient``"""
    global last_query_time

    if (time.time() - last_query_time) < period:
        # print("sleeping between queries", last_query_time+interval-time.time())
        time.sleep(max(last_query_time+interval-time.time(), 0))

    response = self.api_client.search(self.method, **kwargs)
    
    last_query_time = time.time()

    return response

ticketpy.query.BaseQuery._BaseQuery__get = __get

def get_url(self, link):
    """Gets a specific href from '_links' object in a response"""
    # API sometimes return incorrectly-formatted strings, need
    # to parse out parameters and pass them into a new request
    # rather than implicitly trusting the href in _links
    global last_query_time

    if (time.time() - last_query_time) < period:
        # print("sleeping between queries", last_query_time+interval-time.time())
        time.sleep(max(last_query_time+interval-time.time(), 0))

    link = self._parse_link(link)
    resp = ticketpy.client.requests.get(link.url, link.params)

    last_query_time = time.time()

    return ticketpy.client.Page.from_json(self._handle_response(resp))

ticketpy.client.ApiClient.get_url = get_url

@staticmethod
def __success(response):
    """Successful response, just return JSON"""
    json = response.json()
    json['rate'] = {}
    for key, value in response.headers.items():
        if 'rate' not in key.lower():
            continue
        
        json['rate'][key] = value
    
    return json

ticketpy.client.ApiClient._ApiClient__success = __success

class Sale:
    def __init__(self, start, end, tba, tbd, name='Public'):
        self.start = start
        self.end = end
        self.tba = tba
        self.tbd = tbd
        self.name = name
    
    def __repr__(self):
        return f"{self.name}=Start: {self.start} - End: {self.end}"

class Sales:
    def __init__(self, public, presales):
        self.public = public
        self.presales = presales
    
    def __repr__(self):
        return "Sales: \t" + '\n\t'.join(str(s) for s in [self.public, *self.presales])
    
    @staticmethod
    def from_json(json_event):
        public = None
        presales = []
        if 'public' in json_event:
            p = json_event['public']
            try:
                public = Sale(p['startDateTime'], p['endDateTime'], p['startTBA'], p['startTBD'])
            except:
                public = Sale(None, None, None, None)
        
        if 'presales' in json_event:
            p = json_event['presales']
            if isinstance(p, dict):
                p = [p]
            
            presales = [Sale(ps['startDateTime'], ps['endDateTime'], False, False, ps['name']) for ps in p]
        
        return Sales(public, presales)

class Event:
    def __init__(self, event_id=None, name=None, start_date=None,
                 start_time=None, status=None, price_ranges=None, attractions=None,
                 venues=None, utc_datetime=None, classifications=None, sales=None,
                 links=None):
        self.id = event_id
        self.name = name
        #: **Local** start date (*YYYY-MM-DD*)
        self.local_start_date = start_date
        #: **Local** start time (*HH:MM:SS*)
        self.local_start_time = start_time
        #: Sale status (such as *Cancelled, Offsale...*)
        self.status = status
        self.attractions = attractions
        self.classifications = classifications
        self.price_ranges = price_ranges
        self.venues = venues
        self.sales = sales
        self.links = links
        self.__utc_datetime = None
        if utc_datetime is not None:
            self.utc_datetime = utc_datetime

    @property
    def utc_datetime(self):
        """Start date/time in UTC (*YYYY-MM-DDTHH:MM:SSZ*)"""
        return self.__utc_datetime

    @utc_datetime.setter
    def utc_datetime(self, utc_datetime):
        if not utc_datetime:
            self.__utc_datetime = None
        if isinstance(utc_datetime, datetime):
            return
        else:
            ts_format = "%Y-%m-%dT%H:%M:%SZ"
            self.__utc_datetime = datetime.strptime(utc_datetime, ts_format)

    @staticmethod
    def from_json(json_event):
        """Creates an ``Event`` from API's JSON response"""
        e = Event()
        e.json = json_event
        e.id = json_event.get('id')
        e.name = json_event.get('name')

        dates = json_event.get('dates', {})
        start_dates = dates.get('start', {})
        e.local_start_date = start_dates.get('localDate')
        e.local_start_time = start_dates.get('localTime')
        e.utc_datetime = start_dates.get('dateTime') or datetime.fromisoformat(e.local_start_date)

        status = dates.get('status', {})
        e.status = status.get('code')

        if 'classifications' in json_event:
            e.classifications = [ticketpy.model.EventClassification.from_json(cl)
                                 for cl in json_event['classifications']]
        
        if 'attractions' in json_event.get('_embedded', {}):
            e.attractions = [ticketpy.model.Attraction.from_json(cl)
                                 for cl in json_event['_embedded']['attractions']]
        
        if 'sales' in json_event:
            e.sales = Sales.from_json(json_event['sales'])

        price_ranges = []
        if 'priceRanges' in json_event:
            for pr in json_event['priceRanges']:
                if "min" in pr and "max" in pr:
                    price_ranges.append({'min': pr['min'], 'max': pr['max']})
        e.price_ranges = price_ranges

        venues = []
        if 'venues' in json_event.get('_embedded', {}):
            for v in json_event['_embedded']['venues']:
                venues.append(ticketpy.model.Venue.from_json(v))
        e.venues = venues
        ticketpy.model._assign_links(e, json_event)
        return e

    def __str__(self):
        tmpl = ("Event:            {name}\n"
                "Venues:           {venues}\n"
                "Start date:       {local_start_date}\n"
                "Start time:       {local_start_time}\n"
                "Price ranges:     {price_ranges}\n"
                "Sales:            {sales}\n"
                "Status:           {status}\n"
                "Attractions:      {attractions!s}\n"
                "Classifications:  {classifications!s}\n")
        return tmpl.format(**self.__dict__)

ticketpy.model.Event = Event

@staticmethod
def from_json(json_obj):
    """Convert JSON object to ``Attraction`` object"""
    att = ticketpy.model.Attraction()
    att.json = json_obj
    att.id = json_obj.get('id')
    att.name = json_obj.get('name')
    att.url = json_obj.get('url')
    att.test = json_obj.get('test')
    att.images = json_obj.get('images')
    classifications = json_obj.get('classifications', [])
    att.classifications = [
        ticketpy.model.Classification.from_json(cl) for cl in classifications
    ]

    ticketpy.model._assign_links(att, json_obj)
    return att

ticketpy.model.Attraction.from_json = from_json