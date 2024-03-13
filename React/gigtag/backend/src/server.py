import asyncio
from sanic import Sanic, Request, response
from sanic.response import text
from sanic_cors import CORS
from . import middleware, ticketmaster

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

    return response.JSONResponse([a.as_dict() for a in await asyncio.to_thread(request.ctx.user.get_artist_events, json['artist'])])

@app.post("update_user_countries")
async def update_user_countries(request: Request):
    json = request.json
    
    await asyncio.to_thread(request.ctx.user.update_settings, countries=json['countries'])

    return response.HTTPResponse()

@app.after_server_start
async def start_ticketmaster_api(app, loop):
    await ticketmaster.start()
    print("Started Ticketmaster Thread")
