import ticketpy.model

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

