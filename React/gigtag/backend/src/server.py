import asyncio
from sanic import Sanic, Request, response
from sanic.response import text
from sanic_cors import CORS
from . import middleware, ticketmaster, telegram, scheduled

app = Sanic("gigtag-be")

CORS(app=app)
middleware.activate(app=app)

@app.get("user_info")
async def user_info(request: Request):
    return response.JSONResponse(request.ctx.user.as_dict())

@app.get("user_playlists")
async def user_playlists(request: Request):
    playlists = await asyncio.to_thread(request.ctx.user.get_playlists)
    return response.JSONResponse({pl.id: pl.as_dict() for pl in playlists})

@app.get("refresh_playlists")
async def refresh_playlists(request: Request):
    await asyncio.to_thread(request.ctx.user.refresh_playlists)
    playlists = await asyncio.to_thread(request.ctx.user.get_playlists)

    return response.JSONResponse({pl.id: pl.as_dict() for pl in playlists})

@app.post("toggle_playlist")
async def toggle_playlist(request: Request):
    json = request.json

    request.ctx.user.toggle_playlist(id=json['id'], value=json['enabled'])

    return response.HTTPResponse()

@app.post("toggle_artist")
async def toggle_artist(request: Request):
    json = request.json

    request.ctx.user.toggle_artist(name=json['name'], value=json['enabled'])
    return response.HTTPResponse()

@app.get("user_artists")
async def get_artists(request: Request):
    return response.JSONResponse({a.name: a.as_dict() for a in await asyncio.to_thread(request.ctx.user.get_enabled_artists, "fresh" in request.args)})

@app.get("user/settings")
async def user_settings(request: Request):
    return response.JSONResponse(await asyncio.to_thread(request.ctx.user.get_settings))

@app.post("artist_events")
async def artist_events(request: Request):
    json = request.json
    
    if json.get("refresh"):
        await asyncio.to_thread(ticketmaster.update_artist_events_for_one_name, artist=json['artist'])

    return response.JSONResponse(await asyncio.to_thread(request.ctx.user.get_artist_events, json['artist']))

@app.post("update_user")
async def update_user(request: Request):
    json = request.json
    
    if 'id' in json:
        json.pop('id')

    if 'email' in json:
        json.pop('email')


    await asyncio.to_thread(request.ctx.user.update_settings, **json)

    return response.HTTPResponse()

@app.post("bug_report")
async def bug_report(request: Request):
    json = request.json
    
    await asyncio.to_thread(telegram.send_bug_report, text=json['text'])

    return response.HTTPResponse()

@app.post("event_notification")
async def event_notification(request: Request):
    json = request.json
    
    if "user_id" in json:
        json.pop("user_id")

    await asyncio.to_thread(request.ctx.user.set_event_notification, **json)

    return response.HTTPResponse()

@app.get("user_events")
async def user_events(request: Request):
    return response.JSONResponse(await asyncio.to_thread(request.ctx.user.get_country_enabled_events))

@app.get("telegram-login")
async def telegram_login(request: Request):
    path = 'https://oauth.telegram.org/embed/GigTag_bot?origin=http%3A%2F%2F127.0.0.1%3A3000&return_to=http%3A%2F%2F127.0.0.1%3A3000%2F%23&size=large&userpic=true&request_access=write&lang=en'
    import requests
    resp = requests.get(path)
    print(resp, resp.status_code, resp.content)
    return response.html(body=resp.content, status=resp.status_code)

@app.after_server_start
async def start_background_tasks(app, loop):
    await scheduled.start()
