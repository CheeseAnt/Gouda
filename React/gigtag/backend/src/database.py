import sqlite3
from datetime import datetime

con = sqlite3.connect("gigtag.db")
con.row_factory = sqlite3.Row

def create_db():
    cur = con.execute("""
        CREATE TABLE USER (
            id varchar(128) PRIMARY KEY,
            email varchar(256)
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

    con.commit()

    print("Created", cur.fetchall())

def insert_user(user_id: str, email: str):
    cur = con.execute("""
INSERT INTO USER (id, email) values (:user, :email)
                """, {'user':user_id, 'email':email})

    con.commit()

def insert_playlist(user_id: str, id: str, name: str, image_url: str, tracks_url: str, count: int, public: bool, owner: str, type: str, enabled: bool):
    cur = con.execute("""
INSERT INTO PLAYLIST (user_id, id, name, image_url, tracks_url, track_count, public, owner, type, last_updated, enabled)
values (:user_id, :id, :name, :image_url, :tracks_url, :count, :public, :owner, :type, :last_updated, :enabled)
                """, {'user_id': user_id, 'id': id, 'name': name, 'image_url': image_url, 'tracks_url': tracks_url, 'count': count, 'public': public, 'owner': owner, 'type': type, 'enabled': enabled, 'last_updated': datetime.utcnow()})

    con.commit()

    print(cur.fetchall())

def update_playlist(user_id: str, id: str, kwargs: dict):
    kwargs['last_updated'] = datetime.utcnow()
    keys = list(kwargs.keys())

    cur = con.execute(f"""
UPDATE PLAYLIST SET
{",".join(key + '=:' + key for key in keys)}
WHERE user_id=:user_id AND id=:id 
                """, {'user_id': user_id, 'id': id, **kwargs})

    con.commit()

def get_playlist(user_id: str, id: str):
    return con.execute("SELECT * FROM PLAYLIST WHERE user_id=:user_id AND id=:id", {"user_id": user_id, 'id': id}).fetchone()

def get_playlists(user_id: str):
    return con.execute("SELECT * FROM PLAYLIST WHERE user_id=:user_id ORDER BY name ASC", {"user_id": user_id}).fetchall()

def get_user(user_id: str):
    return con.execute("SELECT * FROM USER WHERE id=:user_id", {"user_id": user_id}).fetchone()

if __name__ == '__main__':
    create_db()
