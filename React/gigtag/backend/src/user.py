from __future__ import annotations
from . import database
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
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
class Event():
    artist_id: str
    event_id: str
    event_details: dict
    start: datetime
    onsale: datetime
    presale: datetime
    venue: str
    country: str

    def as_dict(self):
        sd = asdict(self)
        return sd

@dataclass
class Artist():
    user_id: int
    name: str
    tracks: int
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

    def __post_init__(self):
        if not database.get_user(user_id=self.id):
            database.insert_user(user_id=self.id, email=self.email)
    
    def get_settings(self):
        return dict(**database.get_user(user_id=self.id))

    def update_settings(self, **kwargs):
        database.update_user(user_id=self.id, kwargs=kwargs)

    def as_dict(self):
        sd = asdict(self)
        sd.pop("_api")
        sd["playlists"] = self.get_latest_playlists_update()
        sd["artists"] = self.get_latest_artists_update()
        return sd

    def get_playlists(self) -> list[Playlist]:
        if database.get_latest_playlist_update(user_id=self.id) < (datetime.utcnow() - timedelta(days=1)):
            self.refresh_playlists()

        return [Playlist(**playlist) for playlist in database.get_playlists(user_id=self.id)]

    def get_playlist(self, id: str) -> Playlist:
        return Playlist(**database.get_playlist(user_id=self.id, id=id))
    
    def toggle_playlist(self, id: str, value: bool):
        database.update_playlist(user_id=self.id, id=id, kwargs={'enabled': value})
    
    def toggle_artist(self, name: str, value: bool):
        database.update_artist(user_id=self.id, name=name, kwargs={'enabled': value})

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
        
        try:
            playlists.append({
                "id": 0,
                "images": [{"url":'https://misc.scdn.co/liked-songs/liked-songs-64.png'}],
                "tracks": {"total": self._api.current_user_saved_tracks()['total'], "href": ""},
                "name": 'Liked Songs',
                "public": False,
                "owner": {"display_name": self.name},
                "type": "Saved Songs"
            })
        except Exception as ex:
            print("Failed to add personal playlist")

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
        
        database.update_playlist_time(user_id=self.id)
        
    def get_latest_artists_update(self):
        return database.get_latest_artists_update(self.id).strftime('%H:%M %A %d, %B %Y')

    def get_latest_playlists_update(self):
        return database.get_latest_playlist_update(self.id).strftime('%H:%M %A %d, %B %Y')

    def get_enabled_artists(self, fresh: bool=False) -> list[Artist]:
        return [Artist(**row) for row in self._get_enabled_artists(fresh=fresh)]

    def _get_enabled_artists(self, fresh: bool=False):
        existing_artists = database.get_artists(user_id=self.id)

        if not fresh and existing_artists and database.get_latest_artists_update(user_id=self.id) > (datetime.utcnow() - timedelta(minutes=5)):
            return existing_artists

        playlists = [p for p in self.get_playlists() if p.enabled]

        class ArtistCounter:
            def __init__(self):
                self.counts = dict()
            
            def add(self, artist: str):
                if artist in ("", None):
                    return

                self.counts[artist] = self.counts.get(artist, 0) + 1
            
            def update(self, other: ArtistCounter):
                for artist, count in other.counts.items():
                    self.counts[artist] = self.counts.get(artist, 0) + count
            
            def set(self):
                return set(self.counts)
            
            def subset(self, sub: set) -> dict:
                return {k:v for k,v in self.counts.items() if k in sub}

        def get_playlist_artists(playlist_id: str) -> set[str]:
            if playlist_id == "0":
                ret_method = lambda playlist_id, fields, offset, limit: self._api.current_user_saved_tracks(offset=offset, limit=limit)
            else:
                ret_method = self._api.playlist_items

            items = list()

            items_in = True

            while items_in:
                items_in = ret_method(playlist_id=playlist_id, fields='items(track(artists(name)))', offset=len(items), limit=50)

                if not items_in or not items_in['items']:
                    break

                items.extend(items_in['items'])

            artists = ArtistCounter()

            for item in items:
                try:
                    for artist in item['track']['artists']:
                        artists.add(artist['name'])
                except:
                    pass
            
            return artists

        artists = ArtistCounter()

        with ThreadPoolExecutor(max_workers=4) as pool:
            results = [pool.submit(get_playlist_artists, p.id) for p in playlists]

        for result in results:
            artists.update(result.result())

        existings = {artist['name'] for artist in existing_artists}

        artists_set = artists.set()
        to_add = artists_set.difference(existings)
        to_update = artists_set.intersection(existings)
        to_delete = existings.difference(artists_set)

        for artist, tracks in artists.subset(to_add).items():
            database.insert_artist(user_id=self.id, name=artist, tracks=tracks, enabled=True)

        for artist, tracks in artists.subset(to_update).items():
            database.update_artist(user_id=self.id, name=artist, kwargs={'tracks':tracks})

        for artist in to_delete:
            database.delete_artist(user_id=self.id, name=artist)

        database.update_artist_time(user_id=self.id)

        artists = database.get_artists(user_id=self.id)

        return artists

    def get_artist_events(self, artist: str) -> list[Event]:
        return [Event(**row) for row in database.get_artist_events(artist=artist)]
