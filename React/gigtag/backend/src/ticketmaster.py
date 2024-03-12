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

def make_rated_request(func, rate: int = 5, period: int=1, **kwargs) -> list:
    start = time.time()
    interval = (period)/rate

    results = list()
    for page in func(**kwargs):
        print("going", time.time(), page)

        if (time.time()-start) < interval:
            time.sleep(start+interval-time.time())

        start = time.time()

        for obj in page:
            results.append(obj)
        
        if len(results) == 1000:
            break

    return results

def resolve_new_artists(api: ticketpy.ApiClient):
    """
    Get all the artists that are new in the DB that have not been found in TM yet
    """
    artists_to_get = database.get_unique_enabled_artist_no_id()
    print(f"Resolving {len(artists_to_get)} artists")
    
    return
    for artist in artists_to_get:
        found = False
        for page in api.attractions.find(keyword=artist):
            if int(page.json['rate']['Rate-Limit-Available']) < 100:
                print("Cannot continue queries, not enough rate available")
                return
            
            for attraction in page:
                if same_artist(attraction.name, artist):
                    print("Found a match", attraction.name, artist, attraction.id)
                    database.insert_artist_id(name=artist, id=attraction.id)
                    found = True
                    break

            if found:
                break

def get_artist_events(api: ticketpy.ApiClient, chunk: int=50):
    artists = {a['id']: a['name'] for a in database.get_unique_enabled_artist_ids()}
    
    artist_ids = list(artist_ids.keys())
    
    for start_idx in range(0, len(artist_ids), chunk):
        artist_id_chunk = artist_ids[start_idx: start_idx+chunk]
        attraction_ids = ",".join(artist_id_chunk)

        for page in api.events.find(attraction_id=attraction_ids):
            for event in page:
                print(event)
                print(dir(event))
                return
                database.insert_event(
                    artist_id=event
                )

def _start():
    # return
    api = ticketpy.ApiClient(api_key=settings.TICKETMASTER_API_KEY)
    
    # resolve_new_artists(api=api)

    get_artist_events(api=api)
    
    return
    for event in make_rated_request(
                api.events.find,
                country_code="IE",
                onsale_start_date_time=format_time(datetime.utcnow()),
                # onsale_end_date_time=format_time((datetime.utcnow()+timedelta(hours=1))),
                start_date_time=format_time(datetime.utcnow()+timedelta(days=90)),
                size=200
            ):
        print(event.name)

async def start():
    threading.Thread(target=_start, daemon=True).start()    