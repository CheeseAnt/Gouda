from . import ticketmaster, telegram
import threading
import time

def do_regular_ticket_check():
    while True:
        try:
            print("Started ticket check")
            ticketmaster.update_event_ticket_availability()
            telegram.send_notifications_for_tickets()
            print("Finished sending notifications")
        except Exception as ex:
            print("Exception while sending notification:", ex)
            pass

        # sleep for 5 minutes
        time.sleep(60 * 5)

async def start():
    threading.Thread(target=ticketmaster._start, daemon=True).start()
    print("Started Ticketmaster Thread")
    threading.Thread(target=do_regular_ticket_check, daemon=True).start()
    print("Started Telegram Inventory Thread")
    
