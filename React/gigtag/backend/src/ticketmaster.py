import ticketpy
import asyncio
from . import settings, ticketpy_fix
from datetime import datetime, timedelta

def _start():
    api = ticketpy.ApiClient(api_key=settings.TICKETMASTER_API_KEY)


    for page in api.events.find(country_code="IE", onsale_start_date_time=datetime.utcnow().isoformat(), onsale_end_date_time=(datetime.utcnow()+timedelta(days=365)).isoformat()):
        for event in page:
            print(event.name)


async def start():
    await asyncio.to_thread(_start)
