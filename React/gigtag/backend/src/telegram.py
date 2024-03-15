from . import settings, database
import requests
import urllib.parse
import jwt
import json
import hashlib

def get_user_id_from_jwt(token: str) -> str:
    if not token:
        # print(f"User {user_id} {settings['email']} is not logged into telegram")
        return ""

    try:
        # the dot dot is needed because telegram uses a bad jwt
        jwtinfo = jwt.get_unverified_header(token + "..")
        return jwtinfo.get("id", "")
    except Exception as ex:
        print("Exception while decryptin JWT", ex)
        # print(f"User {settings['id']} {settings['email']} has invalid telegram JWT: {ex}")
        return ""

def send_markdown_message(text: str, user_id: str):
    try:
        # resp = requests.get(TELEGRAM_BASIC_URL.format(
        #     secret=settings.TELEGRAM_SECRET,
        #     chatid=user_id,
        #     parse_mode="Markdown",
        #     text=urllib.parse.quote_plus(text),
        # ))
        
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_SECRET}/sendMessage"

        data = {
            "chat_id": user_id,
            "text": text,
            "parse_mode": "MarkdownV2"
        }

        resp = requests.post(url, json=data)
        
        if resp.status_code != 200:
            raise Exception(f"Status not 200: {resp.status_code} {resp.content}")
    except Exception as ex:
        print(f"Failed to send message {text} due to {ex}")
    

def send_bug_report(text: str):
    """
    Send a bug report to the admin

    Args:
        text (str): text of the report
    """
    chat_id = "1428682957"
    send_markdown_message(text=f"\#BUG REPORT:  \n{text}", user_id=chat_id)

def send_message_to_user(user_id: str, text: str):
    settings = database.get_user(user_id=user_id)

    user_id = get_user_id_from_jwt(token=settings['telegramID'])
    if not user_id:
        print(f"User {user_id} {settings['email']} has invalid telegram JWT")

    send_markdown_message(text=text, user_id=user_id)

def send_notifications_for_tickets():
    events = database.get_notification_events()
    for event in events:
        user_id = get_user_id_from_jwt(token=event['telegramID'])
        if not user_id:
            print("Failed to send notification due to bad telegram config")
            continue

        event_details = json.loads(event['event_details'])
        
        hash_string = f"{event['user_id']}-{event['event_id']}"
        message = []
        if event['sale_enabled']:
            hash_string += f"-{event['sale']}-{event['saledate']}"
            message.append(f"General Sale Tickets")
        
        if event['resale_enabled']:
            hash_string += f"-{event['resale']}-{event['resaledate']}"
            message.append(f"Resale Tickets")
            
        notif_hash = hashlib.md5(hash_string.encode()).hexdigest()
        
        if database.has_been_notified(user_id=event['user_id'], hash_string=notif_hash):
            print("Notification already served")
            continue

        url = event_details['url']
        name = event_details['name']
        
        message = " and ".join(message)
        message += f" are available for {name} at [ticketmaster]({url})"
        
        send_markdown_message(text=message, user_id=user_id)        
        