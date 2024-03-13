import sqlite3
import json
from datetime import datetime, timedelta

class Connection:
    def __init__(self, path="gigtag.db"):
        self.path = path

    def __enter__(self):
        self.connection: sqlite3.Connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()

class Duplicate(Exception):
    pass

def create_db():
    with Connection() as con:
        cur = con.execute("""
            CREATE TABLE USER (
                id varchar(128) PRIMARY KEY,
                email varchar(256),
                countries text,
                last_updated_playlists datetime,
                last_updated_artists datetime
            );""")
        
        con.execute("""
            CREATE TABLE PLAYLIST (
                id varchar(256),
                user_id varchar(128),
                name varchar(256),
                image_url varchar(256),
                tracks_url varchar(256),
                track_count integer,
                public bool,
                owner varchar(256),
                type varchar(128),
                last_updated datetime,
                enabled bool,
                FOREIGN KEY (user_id) REFERENCES USER(id),
                PRIMARY KEY (id, user_id)
            );
        """)

        con.execute("""
            CREATE TABLE ARTIST (
                name varchar(256),
                user_id varchar(128),
                last_updated datetime,
                tracks integer,
                enabled bool,
                FOREIGN KEY (user_id) REFERENCES USER(id),
                PRIMARY KEY (name, user_id)
            );
        """)
        
        cur = con.execute("""
            CREATE TABLE ARTIST_ID (
                name varchar(256) PRIMARY KEY,
                id varchar(128)
            );
                          """)
        
        cur = con.execute("""
            CREATE TABLE EVENT (
                artist_id varchar(256),
                event_id varchar(256),
                event_details TEXT,
                start datetime,
                onsale datetime,
                presale datetime,
                venue varchar(256),
                country varchar(64),
                PRIMARY KEY (artist_id, event_id)
            );
        """)

        con.commit()

        print("Created", cur.fetchall())

def insert_user(user_id: str, email: str):
    with Connection() as con:
        cur = con.execute("""
    INSERT INTO USER (id, email, last_updated_playlists, last_updated_artists) values (:user, :email, :p, :a)
                    """, {'user':user_id, 'email':email, 'p': datetime.utcnow()-timedelta(days=1), 'a': datetime.utcnow()-timedelta(days=1)})

        con.commit()

def update_playlist_time(user_id: str):
    with Connection() as con:
        cur = con.execute("UPDATE USER SET last_updated_playlists=:time WHERE id=:user_id", {"time": datetime.utcnow(), "user_id": user_id})
        con.commit()

def update_artist_time(user_id: str):
    with Connection() as con:
        cur = con.execute("UPDATE USER SET last_updated_artists=:time WHERE id=:user_id", {"time": datetime.utcnow(), "user_id": user_id})
        con.commit()

def get_latest_playlist_update(user_id: str):
    with Connection() as con:
        cur = con.execute("""SELECT last_updated_playlists from USER where id=:user_id""", {'user_id':user_id})

        return datetime.fromisoformat(cur.fetchone()[0])

def get_latest_artists_update(user_id: str):
    with Connection() as con:
        cur = con.execute("""SELECT last_updated_artists from USER where id=:user_id""", {'user_id':user_id})

        return datetime.fromisoformat(cur.fetchone()[0])

def insert_playlist(user_id: str, id: str, name: str, image_url: str, tracks_url: str, count: int, public: bool, owner: str, type: str, enabled: bool):
    with Connection() as con:
        cur = con.execute("""
    INSERT INTO PLAYLIST (user_id, id, name, image_url, tracks_url, track_count, public, owner, type, last_updated, enabled)
    values (:user_id, :id, :name, :image_url, :tracks_url, :count, :public, :owner, :type, :last_updated, :enabled)
                    """, {'user_id': user_id, 'id': id, 'name': name, 'image_url': image_url, 'tracks_url': tracks_url, 'count': count, 'public': public, 'owner': owner, 'type': type, 'enabled': enabled, 'last_updated': datetime.utcnow()})

        con.commit()

        cur.fetchall()

def update_playlist(user_id: str, id: str, kwargs: dict):
    with Connection() as con:
        kwargs['last_updated'] = datetime.utcnow()
        keys = list(kwargs.keys())

        cur = con.execute(f"""
    UPDATE PLAYLIST SET
    {",".join(key + '=:' + key for key in keys)}
    WHERE user_id=:user_id AND id=:id 
                    """, {'user_id': user_id, 'id': id, **kwargs})

        con.commit()

def get_playlist(user_id: str, id: str):
    with Connection() as con:
        return con.execute("SELECT * FROM PLAYLIST WHERE user_id=:user_id AND id=:id", {"user_id": user_id, 'id': id}).fetchone()

def get_playlists(user_id: str):
    with Connection() as con:
        return con.execute("SELECT * FROM PLAYLIST WHERE user_id=:user_id ORDER BY name ASC", {"user_id": user_id}).fetchall()

def get_user(user_id: str):
    with Connection() as con:
        return con.execute("SELECT * FROM USER WHERE id=:user_id", {"user_id": user_id}).fetchone()

def insert_artist(user_id: str, name: str, tracks: int, enabled: bool):
    with Connection() as con:
        cur = con.execute("""
    INSERT INTO ARTIST (user_id, name, last_updated, tracks, enabled)
    values (:user_id, :name, :last_updated, :tracks, :enabled)
                    """, {'user_id': user_id, 'name': name, 'enabled': enabled, 'tracks': tracks, 'last_updated': datetime.utcnow()})

        con.commit()

        cur.fetchall()

def insert_artist_id(name: str, id: str):
    with Connection() as con:
        cur = con.execute("""
    INSERT INTO ARTIST_ID (name, id)
    values (:name, :id)
                    """, {'name': name, 'id': id})

        con.commit()

        cur.fetchall()

def update_artist(user_id: str, name: str, kwargs: dict):
    with Connection() as con:
        kwargs['last_updated'] = datetime.utcnow()
        keys = list(kwargs.keys())

        cur = con.execute(f"""
    UPDATE ARTIST SET
    {",".join(key + '=:' + key for key in keys)}
    WHERE user_id=:user_id AND name=:name 
                    """, {'user_id': user_id, 'name': name, **kwargs})

        con.commit()

def get_artists(user_id: str):
    with Connection() as con:
        cur = con.execute(f"""
    SELECT * FROM ARTIST
    WHERE user_id=:user_id
    ORDER BY NAME ASC
                    """, {'user_id': user_id})
        
        return cur.fetchall()

def get_unique_artists():
    with Connection() as con:
        cur = con.execute(f"""SELECT DISTINCT name FROM ARTIST WHERE ENABLED ORDER BY NAME ASC""")
        return cur.fetchall()

def get_unique_enabled_artist_ids():
    with Connection() as con:
        cur = con.execute(f"""SELECT DISTINCT i.id, i.name FROM ARTIST_ID i JOIN ARTIST t ON i.name=t.name WHERE t.enabled""")
        return cur.fetchall()

def get_unique_enabled_artist_no_id():
    with Connection() as con:
        cur = con.execute(f"""SELECT distinct a.name FROM ARTIST a LEFT JOIN ARTIST_ID ai ON a.name=ai.name WHERE a.enabled AND ai.name IS NULL""")
        return [a['name'] for a in cur.fetchall()]

def delete_artist(user_id: str, name: str):
    with Connection() as con:
        cur = con.execute("DELETE FROM ARTIST WHERE user_id=:user_id AND name=:name", {"user_id": user_id, "name": name})
        con.commit()
        cur.fetchall()

def get_events(artist_id: str) -> list[dict]:
    """Fetches all events for a given artist from the database.

    Args:
        artist_id: The artist ID to fetch events for.

    Returns:
        A list of dictionaries representing event details. Each dictionary has keys
        matching the table columns (artist_id, event_id, event_details, onsale,
        presale, venue, country).

    Raises:
        Exception: If an error occurs during database interaction.
    """

    with Connection() as con:
        cur = con.cursor()
        try:
            cur.execute("""
            SELECT * FROM EVENT WHERE artist_id = :artist_id
            """, {'artist_id': artist_id})
            events = cur.fetchall()
        except Exception as e:
            raise Exception(f"Error fetching events for artist {artist_id}: {e}") from e

        events = [dict(row) for row in events]
        for event in events:
            event['event_details'] = json.loads(event['event_details'])

        return events

def insert_event(artist_id: str, event_id: str, event_details: dict, start: datetime,
                 onsale: datetime, presale: datetime, venue: str, country: str) -> None:
    """Inserts a new event into the database.

    Args:
        artist_id: The artist ID for the event.
        event_id: A unique identifier for the event.
        event_details: Textual description or details about the event.
        onsale: Date and time when tickets go on sale (datetime object).
        presale: Date and time for any presale (datetime object, can be None).
        venue: Name of the venue where the event takes place.
        country: The country where the event takes place.

    Raises:
        Exception: If an error occurs during database interaction.
    """
    event_details = json.dumps(event_details)

    with Connection() as con:
        cur = con.cursor()
        try:
            cur.execute("""
            INSERT INTO EVENT (artist_id, event_id, event_details, start, onsale, presale, venue, country)
            VALUES (:artist_id, :event_id, :event_details, :start, :onsale, :presale, :venue, :country)
            """, {'artist_id': artist_id, 'event_id': event_id, 'event_details': event_details,
                'start': start, 'onsale': onsale, 'presale': presale, 'venue': venue, 'country': country})
            con.commit()
        except Exception as e:
            raise Duplicate(f"Error inserting event for artist {artist_id}: {e}") from e

def update_event(artist_id: str, event_id: str, **kwargs: dict):
    with Connection() as con:
        keys = list(kwargs.keys())

        if "event_details" in kwargs:
            kwargs['event_details'] = json.dumps(kwargs['event_details'])

        cur = con.execute(f"""
    UPDATE EVENT SET
    {",".join(key + '=:' + key for key in keys)}
    WHERE artist_id=:artist_id AND event_id=:event_id 
                    """, {'artist_id': artist_id, 'event_id': event_id, **kwargs})

        con.commit()

def get_artist_events(artist: str):
    with Connection() as con:
        cur = con.execute(f"""SELECT DISTINCT id FROM ARTIST_ID WHERE name=:name""", {'name': artist})
        ids = [a['id'] for a in cur.fetchall()]

    events = list()
    for artist_id in ids:
        events.extend(get_events(artist_id=artist_id))

    return events

if __name__ == '__main__':
    # print(get_unique_enabled_artist_ids())
    with Connection() as con:
        # cur = con.execute("ALTER TABLE USER ADD COLUMN countries text")
        # con.commit()
        
        # cur = con.execute("SELECT * FROM ARTIST", {'start': datetime.utcnow()})
        print(cur.fetchall()[0][:])

    # create_db()
