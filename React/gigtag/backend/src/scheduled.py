from . import ticketmaster, telegram
import threading
import time

def do_regular_ticket_check():
    while True:
        try:
            ticketmaster.update_event_ticket_availability()
            telegram.send_notifications_for_tickets()
        except:
            pass

        # sleep for 15 minutes
        time.sleep(60 * 15)

async def start():
    threading.Thread(target=ticketmaster._start, daemon=True).start()
    print("Started Ticketmaster Thread")
    threading.Thread(target=do_regular_ticket_check, daemon=True).start()
    print("Started Telegram Inventory Thread")
    


