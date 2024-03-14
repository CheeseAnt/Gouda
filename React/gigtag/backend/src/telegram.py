from . import settings, database
import requests
import urllib.parse
import jwt

TELEGRAM_BASIC_URL = "https://api.telegram.org/bot{secret}/sendMessage?chat_id={chatid}&parse_mode={parse_mode}&text={text}"

def send_markdown_message(text: str, user_id: str):
    try:
        resp = requests.get(TELEGRAM_BASIC_URL.format(
            secret=settings.TELEGRAM_SECRET,
            chatid=user_id,
            parse_mode="Markdown",
            text=urllib.parse.quote_plus(text),
        ))
        
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
    send_markdown_message(text=f"#BUG REPORT:  \n{text}", user_id=chat_id)

def send_message_to_user(user_id: str, text: str):
    settings = database.get_user(user_id=user_id)
    if not settings['telegramID']:
        print(f"User {user_id} {settings['email']} is not logged into telegram")
        return

    try:
        # the dot dot is needed because telegram uses a bad jwt
        jwtinfo = jwt.decode(settings['telegramID'] + "..", verify=False, algorithms=jwt.algorithms.Any)
        
        send_markdown_message(text=text, user_id=jwtinfo.get("id", ""))
    except Exception as ex:
        print(f"User {user_id} {settings['email']} has invalid telegram JWT: {ex}")

