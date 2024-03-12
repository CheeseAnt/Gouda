import ticketpy.model
import time
from collections import namedtuple

@staticmethod
def from_json(json_event):
    """Creates an ``Event`` from API's JSON response"""
    e = ticketpy.model.Event()
    e.json = json_event
    e.id = json_event.get('id')
    e.name = json_event.get('name')

    dates = json_event.get('dates', {})
    start_dates = dates.get('start', {})
    e.local_start_date = start_dates.get('localDate')
    e.local_start_time = start_dates.get('localTime')
    e.utc_datetime = start_dates.get('dateTime')

    status = dates.get('status', {})
    e.status = status.get('code')

    if 'classifications' in json_event:
        e.classifications = [ticketpy.model.EventClassification.from_json(cl)
                                for cl in json_event['classifications']]

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

ticketpy.model.Event.from_json = from_json

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
