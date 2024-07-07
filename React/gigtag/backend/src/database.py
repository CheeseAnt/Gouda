import pyodbc
import json
import os
from datetime import datetime, timedelta
from multiprocessing import Lock
import re
import hashlib
import typing

def find_parameters(query):
    # Define the regular expression pattern for named parameters
    pattern = r':\w+'
    # Find all matches in the query string
    matches = re.findall(pattern, query)
    return matches

def execute_with_dict(conn, query:str, kwargs=None, *args, **kwargsd):
    if kwargs is None:
        return conn.execute(query, *args, **kwargsd)
    if not isinstance(kwargs, dict):
        return conn.execute(query, kwargs, *args, **kwargsd)
    
    params = find_parameters(query)
    
    values = []
    for param in params:
        pp = param[1:]
        pv = kwargs.get(pp)
        values.append(pv)
        query = query.replace(param, "?", 1)
    
    # print(query, values)
    return conn.execute(query, *values)

# def dictify(row):
#     columns = [column[0] for column in cursordescription]
#     return {columns[index]: value for index, value in enumerate(row)}

class Duplicate(Exception):
    pass

class Connection:
    def __init__(self):
        self.conn_str = os.environ.get("az_conn")

    def __enter__(self):
        self.connection: pyodbc.Connection = pyodbc.connect(f'{self.conn_str};DRIVER={{ODBC Driver 18 for SQL Server}}')
        self.connection.autocommit = False

        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        # pass
        self.connection.close()


def create_db():
    with Connection() as con:
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE "USER" (
                id varchar(128) PRIMARY KEY,
                email varchar(256),
                countries text,
                telegramID text,
                notify_for_gigs bit,
                last_updated_playlists datetime,
                last_updated_artists datetime
            );""")
        
        cur.execute("""
            CREATE TABLE "PLAYLIST" (
                id varchar(256),
                user_id varchar(128),
                name varchar(256),
                image_url varchar(256),
                tracks_url varchar(256),
                track_count integer,
                public_ bit,
                owner varchar(256),
                type varchar(128),
                last_updated datetime,
                enabled bit,
                FOREIGN KEY (user_id) REFERENCES "USER"(id),
                PRIMARY KEY (id, user_id)
            );
        """)

        cur.execute("""
            CREATE TABLE "ARTIST" (
                name varchar(256),
                user_id varchar(128),
                last_updated datetime,
                tracks integer,
                enabled bit,
                FOREIGN KEY (user_id) REFERENCES "USER"(id),
                PRIMARY KEY (name, user_id)
            );
        """)
        
        cur.execute("""
            CREATE TABLE "ARTIST_ID" (
                name varchar(256) PRIMARY KEY,
                id varchar(128)
            );
                          """)
        
        cur.execute("""
            CREATE TABLE "EVENT" (
                event_id varchar(256) PRIMARY KEY,
                event_details TEXT,
                start datetime,
                onsale datetime,
                presale TEXT,
                venue varchar(256),
                country varchar(64),
                checksum varchar(32)
            );
        """)
        
        cur.execute("""
            CREATE TABLE "EVENT_ARTIST" (
                event_id varchar(256),
                artist_id varchar(128),
                FOREIGN KEY (event_id) REFERENCES "EVENT"(event_id) ON DELETE CASCADE,
                UNIQUE (event_id, artist_id)
            );
        """)
        
        cur.execute("""
            CREATE TABLE "USER_EVENT_ENABLE" (
                user_id varchar(256),
                event_id varchar(256),
                sale bit,
                resale bit,
                events text,
                PRIMARY KEY (user_id, event_id)
            );
        """)
        
        cur.execute("""
            CREATE TABLE "USER_NOTIFICATIONS" (
                user_id varchar(256),
                hash varchar(32),
                date datetime,
                PRIMARY KEY (user_id, hash)
            );
        """)
        
        cur.execute("""
            CREATE TABLE "EVENT_STATUS" (
                event_id varchar(256) PRIMARY KEY,
                sale bit,
                resale bit,
                saledate datetime,
                resaledate datetime
            );
        """)


        con.commit()

        print("Created database")

def insert_user(user_id: str, email: str):
    with Connection() as con:
        cur = execute_with_dict(con, """
    INSERT INTO "USER" (id, email, last_updated_playlists, last_updated_artists) values (:user, :email, :p, :a)
                    """, {'user':user_id, 'email':email, 'p': datetime.utcnow()-timedelta(days=1), 'a': datetime.utcnow()-timedelta(days=1)})

        con.commit()

def update_user(user_id: str, kwargs: dict):
    with Connection() as con:
        keys = list(kwargs.keys())

        cur = execute_with_dict(con, f"""
    UPDATE "USER" SET
    {",".join(key + '=:' + key for key in keys)}
    WHERE id=:user_id
                    """, {'user_id': user_id, **kwargs})

        con.commit()

def update_playlist_time(user_id: str):
    with Connection() as con:
        cur = execute_with_dict(con, """UPDATE "USER" SET last_updated_playlists=:time WHERE id=:user_id""", {"time": datetime.utcnow(), "user_id": user_id})
        con.commit()

def update_artist_time(user_id: str):
    with Connection() as con:
        cur = execute_with_dict(con, """UPDATE "USER" SET last_updated_artists=:time WHERE id=:user_id""", {"time": datetime.utcnow(), "user_id": user_id})
        con.commit()

def get_latest_playlist_update(user_id: str):
    with Connection() as con:
        cur = execute_with_dict(con, """SELECT last_updated_playlists from "USER" where id=:user_id""", {'user_id':user_id})

        return cur.fetchone()[0]

def get_latest_artists_update(user_id: str):
    with Connection() as con:
        cur = execute_with_dict(con, """SELECT last_updated_artists from "USER" where id=:user_id""", {'user_id':user_id})

        return cur.fetchone()[0]

def insert_playlist(user_id: str, id: str, name: str, image_url: str, tracks_url: str, count: int, public: bool, owner: str, type: str, enabled: bool):
    with Connection() as con:
        cur = execute_with_dict(con, """
    INSERT INTO PLAYLIST (user_id, id, name, image_url, tracks_url, track_count, public_, owner, type, last_updated, enabled)
    values (:user_id, :id, :name, :image_url, :tracks_url, :count, :public, :owner, :type, :last_updated, :enabled)
                    """, {'user_id': user_id, 'id': id, 'name': name, 'image_url': image_url, 'tracks_url': tracks_url, 'count': count, 'public': public, 'owner': owner, 'type': type, 'enabled': enabled, 'last_updated': datetime.utcnow()})

        con.commit()

        # cur.fetchall()

def update_playlist(user_id: str, id: str, kwargs: dict):
    with Connection() as con:
        kwargs['last_updated'] = datetime.utcnow()
        
        if "public" in kwargs:
            kwargs['public_'] = kwargs.pop("public")
        keys = list(kwargs.keys())

        cur = execute_with_dict(con, f"""
    UPDATE PLAYLIST SET
    {",".join(key + '=:' + key for key in keys)}
    WHERE user_id=:user_id AND id=:id 
                    """, {'user_id': user_id, 'id': id, **kwargs})

        con.commit()

def get_playlist(user_id: str, id: str):
    with Connection() as con:
        return execute_with_dict(con, "SELECT * FROM PLAYLIST WHERE user_id=:user_id AND id=:id", {"user_id": user_id, 'id': id}).fetchone()

def get_playlists(user_id: str):
    with Connection() as con:
        return dictify(execute_with_dict(con, "SELECT * FROM PLAYLIST WHERE user_id=:user_id ORDER BY name ASC", {"user_id": user_id}).fetchall())

def get_user(user_id: str):
    with Connection() as con:
        return dictify(execute_with_dict(con, """SELECT * FROM "USER" WHERE id=:user_id""", {"user_id": user_id}).fetchall())[0]

def insert_artist(user_id: str, name: str, tracks: int, enabled: bool):
    with Connection() as con:
        try:
            cur = execute_with_dict(con, """
        INSERT INTO ARTIST (user_id, name, last_updated, tracks, enabled)
        values (:user_id, :name, :last_updated, :tracks, :enabled)
                        """, {'user_id': user_id, 'name': name, 'enabled': enabled, 'tracks': tracks, 'last_updated': datetime.utcnow()})

            con.commit()
        except pyodbc.IntegrityError:
            pass

        # cur.fetchall()

def insert_artist_id(name: str, id: str):
    with Connection() as con:
        cur = execute_with_dict(con, """
    INSERT INTO ARTIST_ID (name, id)
    values (:name, :id)
                    """, {'name': name, 'id': id})

        con.commit()

        # cur.fetchall()

def update_artist(user_id: str, name: str, kwargs: dict):
    with Connection() as con:
        kwargs['last_updated'] = datetime.utcnow()
        keys = list(kwargs.keys())

        cur = execute_with_dict(con, f"""
    UPDATE ARTIST SET
    {",".join(key + '=:' + key for key in keys)}
    WHERE user_id=:user_id AND name=:name 
                    """, {'user_id': user_id, 'name': name, **kwargs})

        con.commit()

def get_artists(user_id: str):
    with Connection() as con:
        cur = execute_with_dict(con, f"""
    SELECT * FROM ARTIST
    WHERE user_id=:user_id
    ORDER BY NAME ASC
                    """, {'user_id': user_id})
        
        return dictify(cur.fetchall())

def get_unique_artists():
    with Connection() as con:
        cur = execute_with_dict(con, f"""SELECT DISTINCT name FROM ARTIST WHERE ENABLED=1 ORDER BY NAME ASC""")
        return dictify(cur.fetchall())

def get_unique_enabled_artist_ids():
    with Connection() as con:
        cur = execute_with_dict(con, f"""SELECT DISTINCT i.id, i.name FROM ARTIST_ID i JOIN ARTIST t ON i.name=t.name WHERE t.enabled=1""")
        return dictify(cur.fetchall())

def get_artist_id(name: str):
    with Connection() as con:
        cur = execute_with_dict(con, f"""SELECT i.id, i.name FROM ARTIST_ID i WHERE i.name=:name""", {'name': name})
        try:
            return cur.fetchone()
        except:
            return None

def get_unique_enabled_artist_no_id():
    with Connection() as con:
        cur = execute_with_dict(con, f"""SELECT distinct a.name FROM ARTIST a LEFT JOIN ARTIST_ID ai ON a.name=ai.name WHERE a.enabled=1 AND ai.name IS NULL""")
        return [a['name'] for a in dictify(cur.fetchall())]

def delete_artist(user_id: str, name: str):
    with Connection() as con:
        cur = execute_with_dict(con, "DELETE FROM ARTIST WHERE user_id=:user_id AND name=:name", {"user_id": user_id, "name": name})
        con.commit()
        # cur.fetchall()

def dictify(rows: list[pyodbc.Row]):
    return [dict(zip([column[0] for column in row.cursor_description], row))
             for row in rows]

def get_events(user_id: str, artist_id: str) -> list[dict]:
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
    print(artist_id, user_id)
    with Connection() as con:
        try:
            cur = execute_with_dict(con, f"""
                WITH event_artists AS (
                    SELECT distinct ea.event_id, STRING_AGG(ai.name, ',') as artists, min(a.user_id) as user_id
                    FROM ARTIST_ID ai
                    JOIN ARTIST a ON a.name = ai.name
                    JOIN EVENT_ARTIST ea ON ea.artist_id = ai.id
                    WHERE a.enabled=1 AND ai.id=? and a.user_id=?
                    GROUP BY ea.event_id
                )
                SELECT ex.*, ea.artists, uee.sale as sale_n, uee.resale as resale_n
                FROM EVENT ex
                JOIN event_artists ea ON ex.event_id = ea.event_id
                LEFT OUTER JOIN USER_EVENT_ENABLE uee on uee.user_id=ea.user_id AND uee.event_id=ex.event_id
                ORDER BY ex.start;
            """, (artist_id, user_id))
            events = dictify(cur.fetchall())
    
        except Exception as e:
            raise Exception(f"Error fetching events for artist {artist_id}: {e}") from e

        # events = [row for row in events]
        for event in events:
            event['event_details'] = json.loads(event['event_details'])

        return events

def insert_event_artists(event_id: str, artist_ids: list[str]):
    if not artist_ids:
        return

    values = []
    for a_id in artist_ids:
        values.extend([event_id, a_id])    
    sqls = ",\n".join(["(?, ?)"]*len(artist_ids))

    with Connection() as con:
        try:
            execute_with_dict(con, f"""
            MERGE INTO EVENT_ARTIST AS target
            USING (VALUES {sqls}) AS source (event_id, artist_id)
            ON target.event_id = source.event_id AND target.artist_id = source.artist_id
            WHEN NOT MATCHED BY TARGET THEN
                INSERT (event_id, artist_id)
                VALUES (source.event_id, source.artist_id);
            """, *values)
            con.commit()
        except Exception as e:
            print("Exception while inserting event artists", e)
            con.rollback()

def upsert_event(artist_ids: list[str], event_id: str, event_details: dict, start: datetime,
                 onsale: datetime, presale: datetime, venue: str, country: str):
    event_details_str = json.dumps(event_details)
    new_checksum = hashlib.md5(event_details_str.encode()).hexdigest()
    
    old_checksum = get_event_checksum(event_id=event_id)
    
    if new_checksum == old_checksum:
        insert_event_artists(event_id=event_id, artist_ids=artist_ids)
        return
    
    try:
        if not old_checksum:
            insert_event(event_id=event_id, event_details=event_details_str, start=start,
                        onsale=onsale, presale=presale, venue=venue, country=country, checksum=new_checksum)
        else:
            update_event(event_id=event_id, event_details=event_details_str, start=start,
                        onsale=onsale, presale=presale, venue=venue, country=country, checksum=new_checksum)
    except Duplicate:
        update_event(event_id=event_id, event_details=event_details_str, start=start,
                    onsale=onsale, presale=presale, venue=venue, country=country, checksum=new_checksum)
        
    insert_event_artists(event_id=event_id, artist_ids=artist_ids)

def get_event_checksum(event_id: str) -> typing.Optional[str]:
    with Connection() as con:
        try:
            cur = execute_with_dict(con,
                                    """SELECT checksum from EVENT where event_id=:event_id""",
                                    {'event_id': event_id})
            
            return cur.fetchone().checksum
        except Exception as e:
            return

def insert_event(event_id: str, event_details: str, start: datetime,
                 onsale: datetime, presale: datetime, venue: str, country: str, checksum: str) -> None:
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
    with Connection() as con:
        try:
            execute_with_dict(con, """
            INSERT INTO EVENT (event_id, event_details, start, onsale, presale, venue, country, checksum)
            VALUES (:event_id, :event_details, :start, :onsale, :presale, :venue, :country, :checksum)
            """, {'event_id': event_id, 'event_details': event_details,
                'start': start, 'onsale': onsale, 'presale': presale, 'venue': venue, 'country': country, 'checksum': checksum})
            con.commit()
        except Exception as e:
            con.rollback()
            raise Duplicate(f"Error inserting event for event_id {event_id}: {e}") from e

def update_event(event_id: str, **kwargs: dict):
    with Connection() as con:
        keys = list(kwargs.keys())

        cur = execute_with_dict(con, f"""
            UPDATE EVENT SET
            {",".join(key + '=:' + key for key in keys)}
            WHERE event_id=:event_id 
            """, {'event_id': event_id, **kwargs})

        con.commit()

def get_artist_events(user_id: str, artist: str):
    with Connection() as con:
        cur = execute_with_dict(con, f"""SELECT DISTINCT id FROM ARTIST_ID WHERE name=:name""", {'name': artist})
        ids = [a.id for a in cur.fetchall()]

    events = list()
    for artist_id in ids:
        events.extend(get_events(user_id=user_id, artist_id=artist_id))

    return events

def delete_passed_events():
    with Connection() as con:
        now = datetime.utcnow()
        cur = execute_with_dict(con, f"""DELETE FROM USER_EVENT_ENABLE WHERE event_id IN (
  SELECT event_id
  FROM EVENT e
  WHERE e.start <= :now
) """, {'now': now})
        cur = execute_with_dict(con, f"""DELETE FROM EVENT_STATUS WHERE event_id IN (
  SELECT event_id
  FROM EVENT e
  WHERE e.start <= :now
)""", {'now': now})
        cur = execute_with_dict(con, f"""DELETE FROM EVENT WHERE start<=:now""", {'now': now})

        con.commit()

def get_user_country_specific_enabled_events(user_id: str):
    countries = get_user(user_id=user_id)['countries']
    
    if countries:
        countries = countries.split(",")
    else:
        countries = ''

    country_clause = f"ex.country in ({','.join('?'*len(countries))})" if countries else "1=1"

    with Connection() as con:
        cur = execute_with_dict(con, f"""
            WITH event_artists AS (
                SELECT distinct ea.event_id, STRING_AGG(ai.name, ',') as artists, min(a.user_id) as user_id
                FROM ARTIST_ID ai
                JOIN ARTIST a ON a.name = ai.name
                JOIN EVENT_ARTIST ea ON ea.artist_id = ai.id
                WHERE a.enabled=1 AND a.user_id=?
                GROUP BY ea.event_id
            )
            SELECT ex.*, ea.artists, uee.sale as sale_n, uee.resale as resale_n
            FROM EVENT ex
            JOIN event_artists ea ON ex.event_id = ea.event_id
            LEFT OUTER JOIN USER_EVENT_ENABLE uee on uee.user_id=ea.user_id AND uee.event_id=ex.event_id
            WHERE {country_clause}
            ORDER BY ex.start;
        """, (user_id, *countries))
        
        return dictify(cur.fetchall())

def set_event_notification(user_id: str, event_id: str, **kwargs):
    if not kwargs:
        return

    with Connection() as con:
        keys = ",".join(kwargs.keys())
        inserts = ":" + ",:".join(kwargs.keys())

        try:
            cur = execute_with_dict(con, f"INSERT INTO USER_EVENT_ENABLE(user_id, event_id, {keys}) values (:user_id, :event_id, {inserts})",
                              {
                                "user_id": user_id,
                                "event_id": event_id,
                                **kwargs
                               })
            
            con.commit()
            return
        except:
            con.rollback()
        
        update = ",".join(key + "=:" + key for key in kwargs.keys())
        execute_with_dict(con, f"UPDATE USER_EVENT_ENABLE SET {update} WHERE event_id=:event_id AND user_id=:user_id",
                    {
                        "user_id": user_id,
                        "event_id": event_id,
                        **kwargs
                    })
        
        con.commit()

def set_event_status(event_id: str, sale: bool, resale: bool):
    now = datetime.utcnow()

    with Connection() as con:
        try:
            cur = execute_with_dict(con, f"INSERT INTO EVENT_STATUS(event_id, sale, resale, saledate, resaledate) values (:event_id, :sale, :resale, :now, :now)",
                              {
                                "event_id": event_id,
                                "sale": sale,
                                "resale": resale,
                                "now": now
                               })
            
            con.commit()
            return
        except:
            con.rollback()
        
        row = execute_with_dict(con, "SELECT * FROM EVENT_STATUS WHERE event_id=:event_id", {"event_id": event_id}).fetchone()
        sets = []
        if row['sale'] != sale:
            sets.append("sale=:sale,saledate=:now")
        
        if row['resale'] != resale:
            sets.append("resale=:resale,resaledate=:now")
        
        if not sets:
            return
        
        update = ",".join(sets)
        
        execute_with_dict(con, f"UPDATE EVENT_STATUS SET {update} WHERE event_id=:event_id",
                    {
                        "event_id": event_id,
                        "sale": sale,
                        "resale": resale,
                        "now": now
                    })
        
        con.commit()

def get_notif_enabled_events():
    with Connection() as con:
        cur = execute_with_dict(con, f"""SELECT event_id FROM USER_EVENT_ENABLE WHERE sale=1 or resale=1""")
        return [a.event_id for a in cur.fetchall()]

def get_notification_events():
    with Connection() as con:
        # TODO: Look at this logic more in depth
        event_statuses = dictify(execute_with_dict(con, """
                                                         SELECT es.*, e.event_details
                                                         FROM EVENT_STATUS es
                                                         JOIN EVENT e ON es.event_id=e.event_id
                                                         WHERE es.sale=1 or es.resale=1
                                                        """).fetchall())
        event_enables = dictify(execute_with_dict(con, """
                                                        SELECT uee.sale as sale_enabled, uee.resale as resale_enabled, uee.event_id, u.id as user_id, u.telegramID
                                                        FROM USER_EVENT_ENABLE uee
                                                        JOIN "USER" u ON uee.user_id=u.id AND u.telegramID is not null
                                                        WHERE uee.sale=1 or uee.resale=1
                                                        """).fetchall())

        event_enables = {e["event_id"]: e for e in event_enables}

        for event in event_statuses:
            event.update(event_enables.get(event.get("event_id"), {}))

        return event_statuses

        # cur = execute_with_dict(con, f"""SELECT 
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
        res = execute_with_dict(con, "SELECT * FROM USER_NOTIFICATIONS WHERE user_id=:user_id AND hash=:hash", {'user_id': user_id, 'hash': hash_string}).fetchall()

        has_notification = len(res) > 0

        if not has_notification:
            execute_with_dict(con, "INSERT INTO USER_NOTIFICATIONS(user_id, hash, date) values (:user_id, :hash, :date)", {'user_id': user_id, 'hash': hash_string, 'date': datetime.utcnow()})
            con.commit()

        return has_notification

if __name__ == '__main__':
    # print(get_unique_enabled_artist_ids())
    # with Connection() as con:
    #     cur = execute_with_dict(con, "ALTER TABLE USER_EVENT_ENABLE ADD COLUMN sale bool")
    #     cur = execute_with_dict(con, "ALTER TABLE USER_EVENT_ENABLE ADD COLUMN resale bool")
        
    #     con.commit()
        
        # cur = execute_with_dict(con, "SELECT COUNT(*) FROM EVENT", {'start': datetime.utcnow()})
        # print(cur.fetchall()[0][:])
    create_db()
