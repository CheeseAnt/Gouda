import ticketpy
import asyncio
import time
import threading
from . import settings, ticketpy_fix, database
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from functools import partial

def same_artist(artist_one: str, artist_two: str) -> bool:
    return SequenceMatcher(None, artist_one, artist_two).ratio() >= 0.75

def format_time(t: datetime):
    return t.strftime('%Y-%m-%dT%H:%M:%SZ')

def get_or_resolve_artist(api: ticketpy.ApiClient, artist: str) -> str:
    """Get the ID for one artist name

    Args:
        artist (str): Artist Name

    Returns:
        str: Artist ID
    """
    artist_id = database.get_artist_id(name=artist)
    if not artist_id:
        artist_id = resolve_one_artist(api=api, artist=artist)
    
    return artist_id

def get_attraction_events(api: ticketpy.ApiClient, attraction_ids: str):
    """Resolves all the events for a specific set of attractions

    Args:
        attraction_ids (str): Attraction ids in a comma separated string
    """
    for page in api.events.find(attraction_id=attraction_ids, size=200):
        for event in page:
            for attraction in event.attractions:
                print(f"Adding event for artist {attraction.name}, event {event.name} at {event.utc_datetime}")
                
                try:
                    database.insert_event(
                        artist_id=attraction.id,
                        event_id=event.id,
                        event_details=event.json,
                        start=event.utc_datetime,
                        onsale=event.sales.public.start,
                        presale=",".join(p.start for p in event.sales.presales),
                        venue=f"{event.venues[0].city}: {event.venues[0].name}",
                        country=event.venues[0].json['country']['countryCode']
                    )
                except database.Duplicate:
                    database.update_event(
                        artist_id=attraction.id,
                        event_id=event.id,
                        event_details=event.json,
                        start=event.utc_datetime,
                        onsale=event.sales.public.start,
                        presale=",".join(p.start for p in event.sales.presales),
                        venue=f"{event.venues[0].city}: {event.venues[0].name}",
                        country=event.venues[0].json['country']['countryCode']
                    )
                except Exception as ex:
                    print(f"Failed to add event for artist {attraction.name}, event {event.name}: {ex}")

def resolve_one_artist(api: ticketpy.ApiClient, artist: str) -> str:
    """
    Resolve the ID for one artist

    Args:
        artist (str): Artist Name

    Returns:
        str: Artist ID
    """
    for page in api.attractions.find(keyword=artist, size=200):
        if int(page.json['rate']['Rate-Limit-Available']) < 500:
            print("Cannot continue queries, not enough rate available")
            return
        
        for attraction in page:
            if same_artist(attraction.name, artist):
                print("Found a match", attraction.name, artist, attraction.id)
                database.insert_artist_id(name=artist, id=attraction.id)
                return attraction.id

def resolve_new_artists(api: ticketpy.ApiClient):
    """
    Get all the artists that are new in the DB that have not been found in TM yet
    """
    artists_to_get = database.get_unique_enabled_artist_no_id()
    print(f"Resolving {len(artists_to_get)} artists")
    
    for artist in artists_to_get:
        resolve_one_artist(api=api, artist=artist)
        
def get_artist_events(api: ticketpy.ApiClient, chunk: int=50):
    """
    Get all the upcoming events for all enabled artists in the DB

    Args:
        api (ticketpy.ApiClient): ticketmaster Api Object
        chunk (int, optional): Chunk size to get events by. Defaults to 50.
    """
    artists = {a['id']: a['name'] for a in database.get_unique_enabled_artist_ids()}
    
    artist_ids = list(artists.keys())
    
    for start_idx in range(0, len(artist_ids), chunk):
        artist_id_chunk = artist_ids[start_idx: start_idx+chunk]
        attraction_ids = ",".join(artist_id_chunk)

        get_attraction_events(api=api, attraction_ids=attraction_ids)

def update_artist_events_for_one_name(artist: str):
    api = ticketpy.ApiClient(api_key=settings.TICKETMASTER_API_KEY)
    artist_id = get_or_resolve_artist(api=api, artist=artist)
    
    if not artist_id:
        return []

    get_attraction_events(api=api, attraction_ids=artist_id)

class EventTicketsAvailable():
    IN_STOCK = ("TICKETS_AVAILABLE", "FEW_TICKETS_LEFT")
    def __init__(self, event_id: str, sale: str, resale: str):
        self.event_id = event_id
        self.sale = sale in self.IN_STOCK
        self.resale = resale in self.IN_STOCK

INVENTORY_URL = "https://app.ticketmaster.com/inventory-status/v1/availability?events={event_ids}&apikey={api_key}"

def get_event_availability(event_ids: list[str]) -> list[EventTicketsAvailable]:
    """Get event ticket availabilities

    Args:
        event_ids (list[str]): list of event ids

    Returns:
        list[EventTicketsAvailable]: List of events and their ticket availabilities
    """
    
    tickets = list()
    for first_idx in range(0, len(event_ids), 1000):
        subset = ",".join(event_ids[first_idx: first_idx+1000])
        print("Making inventory request")
        response = ticketpy_fix.rated_request(
            url=INVENTORY_URL.format(
                event_ids=subset,
                api_key=settings.TICKETMASTER_API_KEY
            ))
        if response.status_code != 200:
            print("Failed to make request to ticketmaster inventory")
            continue

        json = response.json()
        
        tickets.extend([EventTicketsAvailable(event_id=j['eventId'], sale=j['status'], resale=j['resaleStatus']) for j in json])

    return tickets

def update_event_ticket_availability():
    print("Getting enabled events")
    event_ids = database.get_notif_enabled_events()
    print("Getting inventory status", event_ids)
    event_tickets = get_event_availability(event_ids=event_ids)
    
    print("Setting database fields")
    for event_ticket in event_tickets:
        database.set_event_status(event_id=event_ticket.event_id, sale=event_ticket.sale, resale=event_ticket.resale)

    print("Updated event tickets availability")

def sleep_until(target_time: str):
    # Get current time
    current_time = datetime.now()
    
    hour, minute = target_time.split(":")
    hour = int(hour)
    minute = int(minute)
    target_datetime = current_time.replace(hour=hour, minute=minute, second=0)

    # Calculate time difference (considering date change if necessary)
    time_diff = target_datetime - current_time
    if time_diff.days < 0:  # Target time is next day
      time_diff += timedelta(days=1)

    # Convert time difference to seconds and sleep
    sleep_duration = time_diff.total_seconds()
    print(f"Sleeping for {sleep_duration:.2f} seconds to reach {target_time}.")
    time.sleep(sleep_duration)

def _start():
    # return
    api = ticketpy.ApiClient(api_key=settings.TICKETMASTER_API_KEY)
    
    while True:
        try:
            print("Getting new artists")
            resolve_new_artists(api=api)
            print("Getting events")
            get_artist_events(api=api)
            print("Deleting old events")
            database.delete_passed_events()
        except Exception as ex:
            print(f"Hit problem: {ex} while scheduled pulling")
            pass

        sleep_until("15:30")
