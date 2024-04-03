import sqlite3
import json
from datetime import datetime, timedelta
from multiprocessing import Lock

_lock = Lock()

def locked_commit(con, attempt: int=0):
    try:
        con.commit()
    except:
        if attempt > 3:
            raise
        return locked_commit(con=con, attempt=attempt+1)


class Connection:
    def __init__(self, path="data/gigtag.db"):
        self.path = path

    def __enter__(self):
        self.connection: sqlite3.Connection = sqlite3.connect(self.path, timeout=30)
        self.connection.row_factory = sqlite3.Row

        _lock.acquire()
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()
        _lock.release()

class Duplicate(Exception):
    pass

def create_db():
    with Connection() as con:
        cur = con.execute("""
            CREATE TABLE USER (
                id varchar(128) PRIMARY KEY,
                email varchar(256),
                countries text,
                telegramID text,
                notify_for_gigs bool,
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
        
        cur = con.execute("""
            CREATE TABLE USER_EVENT_ENABLE (
                user_id varchar(256),
                event_id varchar(256),
                sale bool,
                resale bool,
                events text,
                PRIMARY KEY (user_id, event_id)
            );
        """)
        
        cur = con.execute("""
            CREATE TABLE USER_NOTIFICATIONS (
                user_id varchar(256),
                hash varchar(32),
                date datetime,
                PRIMARY KEY (user_id, hash)
            );
        """)
        
        cur = con.execute("""
            CREATE TABLE EVENT_STATUS (
                event_id varchar(256) PRIMARY KEY,
                sale bool,
                resale bool,
                saledate datetime,
                resaledate datetime
            );
        """)


        locked_commit(con)

        print("Created", cur.fetchall())

def insert_user(user_id: str, email: str):
    with Connection() as con:
        cur = con.execute("""
    INSERT INTO USER (id, email, last_updated_playlists, last_updated_artists) values (:user, :email, :p, :a)
                    """, {'user':user_id, 'email':email, 'p': datetime.utcnow()-timedelta(days=1), 'a': datetime.utcnow()-timedelta(days=1)})

        locked_commit(con)

def update_user(user_id: str, kwargs: dict):
    with Connection() as con:
        keys = list(kwargs.keys())

        cur = con.execute(f"""
    UPDATE USER SET
    {",".join(key + '=:' + key for key in keys)}
    WHERE id=:user_id
                    """, {'user_id': user_id, **kwargs})

        locked_commit(con)

def update_playlist_time(user_id: str):
    with Connection() as con:
        cur = con.execute("UPDATE USER SET last_updated_playlists=:time WHERE id=:user_id", {"time": datetime.utcnow(), "user_id": user_id})
        locked_commit(con)

def update_artist_time(user_id: str):
    with Connection() as con:
        cur = con.execute("UPDATE USER SET last_updated_artists=:time WHERE id=:user_id", {"time": datetime.utcnow(), "user_id": user_id})
        locked_commit(con)

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

        locked_commit(con)

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

        locked_commit(con)

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

        locked_commit(con)

        cur.fetchall()

def insert_artist_id(name: str, id: str):
    with Connection() as con:
        cur = con.execute("""
    INSERT INTO ARTIST_ID (name, id)
    values (:name, :id)
                    """, {'name': name, 'id': id})

        locked_commit(con)

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

        locked_commit(con)

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

def get_artist_id(name: str):
    with Connection() as con:
        cur = con.execute(f"""SELECT i.id, i.name FROM ARTIST_ID i WHERE i.name=:name""", {'name': name})
        try:
            return cur.fetchone()
        except:
            return None

def get_unique_enabled_artist_no_id():
    with Connection() as con:
        cur = con.execute(f"""SELECT distinct a.name FROM ARTIST a LEFT JOIN ARTIST_ID ai ON a.name=ai.name WHERE a.enabled AND ai.name IS NULL""")
        return [a['name'] for a in cur.fetchall()]

def delete_artist(user_id: str, name: str):
    with Connection() as con:
        cur = con.execute("DELETE FROM ARTIST WHERE user_id=:user_id AND name=:name", {"user_id": user_id, "name": name})
        locked_commit(con)
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
            SELECT e.*,
                GROUP_CONCAT(ai.name, ', ') AS artists,
                uee.sale as sale_n,
                uee.resale as resale_n
            FROM EVENT e
            JOIN ARTIST_ID ai ON e.artist_id = ai.id AND e.artist_id = :artist_id
            LEFT OUTER JOIN USER_EVENT_ENABLE uee ON uee.event_id = e.event_id
            GROUP BY e.event_id, ai.name
            ORDER BY e.start
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
            locked_commit(con)
        except Exception as e:
            con.rollback()
            con.close()
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

        locked_commit(con)

def get_artist_events(artist: str):
    with Connection() as con:
        cur = con.execute(f"""SELECT DISTINCT id FROM ARTIST_ID WHERE name=:name""", {'name': artist})
        ids = [a['id'] for a in cur.fetchall()]

    events = list()
    for artist_id in ids:
        events.extend(get_events(artist_id=artist_id))

    return events

def delete_passed_events():
    with Connection() as con:
        now = datetime.utcnow()
        cur = con.execute(f"""DELETE FROM USER_EVENT_ENABLE WHERE event_id IN (
  SELECT event_id
  FROM EVENT e
  WHERE e.start <= :now
) """, {'now': now})
        cur = con.execute(f"""DELETE FROM EVENT_STATUS WHERE event_id IN (
  SELECT event_id
  FROM EVENT e
  WHERE e.start <= :now
)""", {'now': now})
        cur = con.execute(f"""DELETE FROM EVENT WHERE start<=:now""", {'now': now})

        locked_commit(con)

def get_user_country_specific_enabled_events(user_id: str):
    countries = get_user(user_id=user_id)['countries']
    
    if countries:
        countries = countries.split(",")
    else:
        countries = ''

    country_clause = f"e.country in ({','.join('?'*len(countries))})" if countries else "1"

    with Connection() as con:
        cur = con.execute(f"""
        SELECT e.*,
            GROUP_CONCAT(a.name, ', ') AS artists,
            uee.sale as sale_n,
            uee.resale as resale_n
        FROM EVENT e
        JOIN ARTIST_ID ai ON e.artist_id = ai.id
        JOIN ARTIST a ON a.name = ai.name
        LEFT OUTER JOIN USER_EVENT_ENABLE uee ON uee.event_id = e.event_id
        WHERE a.enabled AND {country_clause} AND a.user_id=?
        GROUP BY e.event_id, ai.name
        ORDER BY e.start
        """, (*countries, user_id))
        
        return [dict(**row) for row in cur.fetchall()]

def set_event_notification(user_id: str, event_id: str, **kwargs):
    if not kwargs:
        return

    with Connection() as con:
        keys = ",".join(kwargs.keys())
        inserts = ":" + ",:".join(kwargs.keys())

        try:
            cur = con.execute(f"INSERT INTO USER_EVENT_ENABLE(user_id, event_id, {keys}) values (:user_id, :event_id, {inserts})",
                              {
                                "user_id": user_id,
                                "event_id": event_id,
                                **kwargs
                               })
            
            locked_commit(con)
            return
        except:
            con.rollback()
        
        update = ",".join(key + "=:" + key for key in kwargs.keys())
        con.execute(f"UPDATE USER_EVENT_ENABLE SET {update} WHERE event_id=:event_id AND user_id=:user_id",
                    {
                        "user_id": user_id,
                        "event_id": event_id,
                        **kwargs
                    })
        
        locked_commit(con)

def set_event_status(event_id: str, sale: bool, resale: bool):
    now = datetime.utcnow()

    with Connection() as con:
        try:
            cur = con.execute(f"INSERT INTO EVENT_STATUS(event_id, sale, resale, saledate, resaledate) values (:event_id, :sale, :resale, :now, :now)",
                              {
                                "event_id": event_id,
                                "sale": sale,
                                "resale": resale,
                                "now": now
                               })
            
            locked_commit(con)
            return
        except:
            con.rollback()
        
        row = con.execute("SELECT * FROM EVENT_STATUS WHERE event_id=:event_id", {"event_id": event_id}).fetchone()
        sets = []
        if row['sale'] != sale:
            sets.append("sale=:sale,saledate=:now")
        
        if row['resale'] != resale:
            sets.append("resale=:resale,resaledate=:now")
        
        if not sets:
            return
        
        update = ",".join(sets)
        
        con.execute(f"UPDATE EVENT_STATUS SET {update} WHERE event_id=:event_id",
                    {
                        "event_id": event_id,
                        "sale": sale,
                        "resale": resale,
                        "now": now
                    })
        
        locked_commit(con)

def get_notif_enabled_events():
    with Connection() as con:
        cur = con.execute(f"""SELECT event_id FROM USER_EVENT_ENABLE WHERE sale or resale""")
        return [a['event_id'] for a in cur.fetchall()]

def get_notification_events():
    with Connection() as con:
        event_statuses = [dict(**a) for a in con.execute("""
                                                         SELECT es.*, e.event_details
                                                         FROM EVENT_STATUS es
                                                         JOIN EVENT e ON es.event_id=e.event_id
                                                         WHERE es.sale or es.resale
                                                        """).fetchall()]
        event_enables = [dict(**a) for a in con.execute("""
                                                        SELECT uee.sale as sale_enabled, uee.resale as resale_enabled, uee.event_id, u.id as user_id, u.telegramID
                                                        FROM USER_EVENT_ENABLE uee
                                                        JOIN USER u ON uee.user_id=u.id AND u.telegramID is not null
                                                        WHERE uee.sale or uee.resale
                                                        """).fetchall()]

        event_enables = {e["event_id"]: e for e in event_enables}

        for event in event_statuses:
            event.update(event_enables.get(event.get("event_id"), {}))

        return event_statuses

        # cur = con.execute(f"""SELECT 
        #                     es.*,
        #                     uee.sale as sale_enabled,
        #                     uee.resale as resale_enabled,
        #                     u.telegramID,
        #                     u.id as user_id,
        #                     e.event_details
        #                   FROM EVENT_STATUS es
        #                   JOIN USER_EVENT_ENABLE uee ON uee.event_id=es.event_id AND (uee.sale=es.sale OR uee.resale=es.resale)
        #                   JOIN USER u ON uee.user_id=u.id AND u.telegramID is not null
        #                   JOIN EVENT e ON es.event_id=e.event_id
        #                   WHERE es.sale or es.resale""")

        # return [dict(**a) for a in cur.fetchall()]

def has_been_notified(user_id: str, hash_string: str) -> bool:
    with Connection() as con:
        res = con.execute("SELECT * FROM USER_NOTIFICATIONS WHERE user_id=:user_id AND hash=:hash", {'user_id': user_id, 'hash': hash_string}).fetchall()

        has_notification = len(res) > 0

        if not has_notification:
            con.execute("INSERT INTO USER_NOTIFICATIONS(user_id, hash, date) values (:user_id, :hash, :date)", {'user_id': user_id, 'hash': hash_string, 'date': datetime.utcnow()})
            locked_commit(con)

        return has_notification

if __name__ == '__main__':
    # print(get_unique_enabled_artist_ids())
    # with Connection() as con:
    #     cur = con.execute("ALTER TABLE USER_EVENT_ENABLE ADD COLUMN sale bool")
    #     cur = con.execute("ALTER TABLE USER_EVENT_ENABLE ADD COLUMN resale bool")
        
    #     locked_commit(con)
        
        # cur = con.execute("SELECT COUNT(*) FROM EVENT", {'start': datetime.utcnow()})
        # print(cur.fetchall()[0][:])
    create_db()
