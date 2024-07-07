from pymongo import MongoClient
from datetime import datetime, timedelta
import uuid
import os

# Replace with your Azure Cosmos DB MongoDB connection string
COSMOS_CONNECTION_STRING = os.environ.get("cosmo_str")
DATABASE_NAME = 'gigtag'

client = MongoClient(COSMOS_CONNECTION_STRING)
database = client[DATABASE_NAME]

def get_collection(collection_name):
    return database[collection_name]

def create_db():
    collections = [
        'USER', 'PLAYLIST', 'ARTIST', 'ARTIST_ID', 'EVENT',
        'USER_EVENT_ENABLE', 'USER_NOTIFICATIONS', 'EVENT_STATUS'
    ]
    for collection_name in collections:
        get_collection(collection_name)
    print("Database and collections initialized")

def insert_user(user_id: str, email: str):
    collection = get_collection('USER')
    user = {
        '_id': user_id,
        'email': email,
        'last_updated_playlists': datetime.utcnow() - timedelta(days=1),
        'last_updated_artists': datetime.utcnow() - timedelta(days=1)
    }
    collection.replace_one({'_id': user_id}, user, upsert=True)

def update_user(user_id: str, kwargs: dict):
    collection = get_collection('USER')
    kwargs['last_updated_playlists'] = kwargs.get('last_updated_playlists', datetime.utcnow())
    kwargs['last_updated_artists'] = kwargs.get('last_updated_artists', datetime.utcnow())
    collection.update_one({'_id': user_id}, {'$set': kwargs})

def update_playlist_time(user_id: str):
    update_user(user_id, {'last_updated_playlists': datetime.utcnow()})

def update_artist_time(user_id: str):
    update_user(user_id, {'last_updated_artists': datetime.utcnow()})

def get_latest_playlist_update(user_id: str):
    collection = get_collection('USER')
    user = collection.find_one({'_id': user_id})
    return user['last_updated_playlists']

def get_latest_artists_update(user_id: str):
    collection = get_collection('USER')
    user = collection.find_one({'_id': user_id})
    return user['last_updated_artists']

def insert_playlist(user_id: str, id: str, name: str, image_url: str, tracks_url: str, count: int, public: bool, owner: str, type: str, enabled: bool):
    collection = get_collection('PLAYLIST')
    playlist = {
        '_id': id,
        'user_id': user_id,
        'name': name,
        'image_url': image_url,
        'tracks_url': tracks_url,
        'track_count': count,
        'public': public,
        'owner': owner,
        'type': type,
        'last_updated': datetime.utcnow(),
        'enabled': enabled
    }
    collection.replace_one({'_id': id}, playlist, upsert=True)

def update_playlist(user_id: str, id: str, kwargs: dict):
    collection = get_collection('PLAYLIST')
    kwargs['last_updated'] = datetime.utcnow()
    collection.update_one({'_id': id}, {'$set': kwargs})

def get_playlist(user_id: str, id: str):
    collection = get_collection('PLAYLIST')
    return collection.find_one({'_id': id})

def get_playlists(user_id: str):
    collection = get_collection('PLAYLIST')
    return list(collection.find({'user_id': user_id}).sort('name', 1))

def get_user(user_id: str):
    collection = get_collection('USER')
    return collection.find_one({'_id': user_id})

def insert_artist(user_id: str, name: str, tracks: int, enabled: bool):
    collection = get_collection('ARTIST')
    artist = {
        '_id': f'{user_id}_{name}',
        'user_id': user_id,
        'name': name,
        'last_updated': datetime.utcnow(),
        'tracks': tracks,
        'enabled': enabled
    }
    collection.replace_one({'_id': f'{user_id}_{name}'}, artist, upsert=True)

def insert_artist_id(name: str, id: str):
    collection = get_collection('ARTIST_ID')
    artist_id = {
        '_id': name,
        'name': name,
        'artist_id': id
    }
    collection.replace_one({'_id': name}, artist_id, upsert=True)

def update_artist(user_id: str, name: str, kwargs: dict):
    collection = get_collection('ARTIST')
    artist_id = f'{user_id}_{name}'
    kwargs['last_updated'] = datetime.utcnow()
    collection.update_one({'_id': artist_id}, {'$set': kwargs})

def get_artists(user_id: str):
    collection = get_collection('ARTIST')
    return list(collection.find({'user_id': user_id}).sort('name', 1))

def get_unique_artists():
    collection = get_collection('ARTIST')
    return list(collection.distinct('name', {'enabled': True}))

def get_unique_enabled_artist_ids():
    collection = get_collection('ARTIST_ID')
    artist_collection = get_collection('ARTIST')
    artist_ids = artist_collection.distinct('name', {'enabled': True})
    return list(collection.find({'name': {'$in': artist_ids}}))

def get_artist_id(name: str):
    collection = get_collection('ARTIST_ID')
    return collection.find_one({'_id': name})

def get_unique_enabled_artist_no_id():
    collection = get_collection('ARTIST')
    artist_id_collection = get_collection('ARTIST_ID')
    artists_with_id = artist_id_collection.distinct('name')
    return list(collection.find({'enabled': True, 'name': {'$nin': artists_with_id}}))

def delete_artist(user_id: str, name: str):
    collection = get_collection('ARTIST')
    artist_id = f'{user_id}_{name}'
    collection.delete_one({'_id': artist_id})

def get_events(user_id: str, artist_id: str):
    collection = get_collection('EVENT')
    query = [
        {'$match': {'artist_id': artist_id}},
        {'$lookup': {
            'from': 'ARTIST_ID',
            'localField': 'artist_id',
            'foreignField': 'id',
            'as': 'artists'
        }},
        {'$lookup': {
            'from': 'USER_EVENT_ENABLE',
            'let': {'event_id': '$event_id', 'user_id': user_id},
            'pipeline': [
                {'$match': {
                    '$expr': {
                        '$and': [
                            {'$eq': ['$event_id', '$$event_id']},
                            {'$eq': ['$user_id', '$$user_id']}
                        ]
                    }
                }}
            ],
            'as': 'user_event_enable'
        }},
        {'$unwind': '$artists'},
        {'$project': {
            'event_details': 1,
            'start': 1,
            'onsale': 1,
            'presale': 1,
            'venue': 1,
            'country': 1,
            'artists.name': 1,
            'sale_n': {'$arrayElemAt': ['$user_event_enable.sale', 0]},
            'resale_n': {'$arrayElemAt': ['$user_event_enable.resale', 0]}
        }},
        {'$sort': {'start': 1}}
    ]
    events = list(collection.aggregate(query))
    for event in events:
        event['event_details'] = json.loads(event['event_details'])
    return events

def insert_event(artist_id: str, event_id: str, event_details: dict, start: datetime, onsale: datetime, presale: datetime, venue: str, country: str):
    collection = get_collection('EVENT')
    event = {
        '_id': event_id,
        'artist_id': artist_id,
        'event_details': json.dumps(event_details),
        'start': start,
        'onsale': onsale,
        'presale': presale if presale else None,
        'venue': venue,
        'country': country
    }
    collection.replace_one({'_id': event_id}, event, upsert=True)

def update_event(artist_id: str, event_id: str, kwargs: dict):
    collection = get_collection('EVENT')
    if 'event_details' in kwargs:
        kwargs['event_details'] = json.dumps(kwargs['event_details'])
    collection.update_one({'_id': event_id}, {'$set': kwargs})

def insert_event_status(event_id: str, status: str):
    collection = get_collection('EVENT_STATUS')
    event_status = {
        '_id': event_id,
        'event_id': event_id,
        'status': status
    }
    collection.replace_one({'_id': event_id}, event_status, upsert=True)

def get_event_status(event_id: str):
    collection = get_collection('EVENT_STATUS')
    return collection.find_one({'_id': event_id})

def insert_user_event_enable(user_id: str, event_id: str, sale: bool, resale: bool):
    collection = get_collection('USER_EVENT_ENABLE')
    user_event_enable = {
        '_id': f'{user_id}_{event_id}',
        'user_id': user_id,
        'event_id': event_id,
        'sale': sale,
        'resale': resale
    }
    collection.replace_one({'_id': f'{user_id}_{event_id}'}, user_event_enable, upsert=True)

def insert_notification(user_id: str, message: str, title: str):
    collection = get_collection('USER_NOTIFICATIONS')
    notification = {
        '_id': str(uuid.uuid4()),  # Generate a unique ID for the notification
        'user_id': user_id,
        'message': message,
        'title': title,
        'timestamp': datetime.utcnow()
    }
    collection.insert_one(notification)

def get_notifications(user_id: str):
    collection = get_collection('USER_NOTIFICATIONS')
    return list(collection.find({'user_id': user_id}).sort('timestamp', -1))

# Ensure the database and collections are created
if __name__ == '__main__':
    create_db()
