import sanic, sanic.response
import spotipy
from . import user

class InvalidToken(Exception):
    def __init__(self):
        super().__init__("Token provided as user auth was incorrect")

_cache = {}

def get_user(auth_token: str) -> user.User:
    if auth_token in _cache:
        return _cache[auth_token]

    api = spotipy.client.Spotify(auth=auth_token)

    try:
        user_info = api.current_user()
        
        if not user_info:
            raise InvalidToken()
        
        _cache[auth_token] = user.User(
            id=user_info['id'],
            name=user_info['display_name'],
            email=user_info['email'],
            photo_url=user_info['images'][-1]['url'],
            _api=api
        )

        return _cache[auth_token]

    except Exception as ex:
        print("Failed to process user info", ex)
        raise InvalidToken()

def activate(app: sanic.Sanic):
    @app.on_request
    def has_spotify_token(request: sanic.Request):
        if request.path == '/telegram-login':
            return

        _process_request(request=request)

        if not request.ctx.user:
            return sanic.response.HTTPResponse(status=401)

def _process_request(request: sanic.Request):
    request.ctx.user = None

    header = request.headers.get("Authorization", "")

    if not header.startswith("Bearer "):
        return
    
    token = header[7:]

    try:
        request.ctx.user = get_user(auth_token=token)
    except InvalidToken:
        return
