from sanic import Sanic, Request, response
from sanic.response import text
from sanic_cors import CORS
from . import middleware

app = Sanic("gigtag-be")

CORS(app=app)
middleware.activate(app=app)

@app.get("user_info")
async def user_info(request: Request):
    return response.JSONResponse(request.ctx.user.as_dict())

@app.get("user_playlists")
async def user_playlists(request: Request):
    return response.JSONResponse({pl.id: pl.as_dict() for pl in request.ctx.user.get_playlists()})

@app.get("refresh_playlists")
async def refresh_playlists(request: Request):
    request.ctx.user.refresh_playlists()
    return response.JSONResponse({pl.id: pl.as_dict() for pl in request.ctx.user.get_playlists()})

@app.post("toggle_playlist")
async def toggle_playlist(request: Request):
    json = request.json

    request.ctx.user.toggle_playlist(id=json['id'], value=json['enabled'])

    return response.HTTPResponse()
