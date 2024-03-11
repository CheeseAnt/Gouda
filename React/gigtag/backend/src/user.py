from . import database
from dataclasses import dataclass, asdict
from datetime import datetime
import spotipy

@dataclass
class Playlist():
    id: str
    user_id: int
    name: str
    image_url: str
    tracks_url: str
    track_count: int
    public: bool
    owner: str
    type: str
    last_updated: datetime
    enabled: bool
    
    def as_dict(self):
        sd = asdict(self)
        return sd

@dataclass
class User():
    id: str
    name: str
    email: str
    photo_url: str
    _api: spotipy.client.Spotify

    def as_dict(self):
        sd = asdict(self)
        sd.pop("_api")
        return sd

    def get_playlists(self) -> list[Playlist]:
        return [Playlist(**playlist) for playlist in database.get_playlists(user_id=self.id)]

    def get_playlist(self, id: str) -> Playlist:
        return Playlist(**database.get_playlist(user_id=self.id, id=id))
    
    def toggle_playlist(self, id: str, value: bool):
        database.update_playlist(user_id=self.id, id=id, kwargs={'enabled': value})

    def refresh_playlists(self):
        response = self._api.current_user_playlists()

        if not response:
            return
        playlists = list()
        playlists.extend(response['items'])
    
        while len(playlists) != response['total']:
            response = self._api.current_user_playlists(offset=len(playlists))
            if not response:
                return
            playlists.extend(response['items'])

        for playlist in playlists:
            if database.get_playlist(user_id=self.id, id=playlist['id']):
                database.update_playlist(
                    user_id=self.id,
                    id=playlist['id'],
                    kwargs={
                        'image_url': playlist['images'][0]['url'],
                        'track_count': playlist['tracks']['total'],
                    }
                )
                continue

            database.insert_playlist(
                user_id=self.id,
                id=playlist['id'],
                name=playlist['name'],
                image_url=playlist['images'][0]['url'],
                tracks_url=playlist['tracks']['href'],
                count=playlist['tracks']['total'],
                public=playlist['public'],
                owner=playlist['owner']['display_name'],
                type=playlist['type'],
                enabled=False
            )
