import sqlite3
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

def create_db():
    with Connection() as con:
        cur = con.execute("""
            CREATE TABLE USER (
                id varchar(128) PRIMARY KEY,
                email varchar(256),
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
                enabled bool,
                FOREIGN KEY (user_id) REFERENCES USER(id),
                PRIMARY KEY (name, user_id)
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

def insert_artist(user_id: str, name: str, enabled: bool):
    with Connection() as con:
        cur = con.execute("""
    INSERT INTO ARTIST (user_id, name, last_updated, enabled)
    values (:user_id, :name, :last_updated, :enabled)
                    """, {'user_id': user_id, 'name': name, 'enabled': enabled, 'last_updated': datetime.utcnow()})

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

def delete_artist(user_id: str, name: str):
    with Connection() as con:
        cur = con.execute("DELETE FROM ARTIST WHERE user_id=:user_id AND name=:name", {"user_id": user_id, "name": name})
        con.commit()
        cur.fetchall()

if __name__ == '__main__':
    create_db()
