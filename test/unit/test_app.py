import os
import pytest
from dotenv import load_dotenv
from app import app, db, Song

load_dotenv()

SONG_DB = os.getenv('SONG_DB')
ULTRASTAR_DB = os.getenv('ULTRASTAR_DB')

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = SONG_DB
    app.config['SQLALCHEMY_BINDS'] = {
        'us_db': ULTRASTAR_DB
    }
    client = app.test_client()

    with app.app_context():
        db.create_all()

    yield client

# pretty sure this will drop our songs table, and since we're only using an in-memory db..
#    with app.app_context():
#        db.drop_all()


def test_index(client):
    response = client.get('/')
    assert response.status_code == 200


def test_api_songs(client):
    response = client.get('/api/songs')
    assert response.status_code == 200
    assert 'songs' in response.get_json()


def test_api_mp3(client):
    # Add necessary test data to the database
    with app.app_context():
        test_song = Song(
            title='Lose yourself',
            artist='Eminem',
            language='English',
            year=2022,
            mp3_path='Eminem - Lose yourself/Eminem - Lose yourself.mp3',
            modify_date=123456789,
            folder_path='Eminem - Lose yourself'
        )
        db.session.add(test_song)
        db.session.commit()

    response = client.get('/api/mp3', query_string={'mp3_path': 'Eminem - Lose yourself/Eminem - Lose yourself.mp3'})
    assert response.status_code == 200
    assert response.content_type == 'audio/mp3'


def test_handle_song_request(client):
    # Add necessary test data to the database
    with app.app_context():
        test_song = Song(
            title='Basket Case',
            artist='Green Day',
            language='English',
            year=2022,
            mp3_path='green_day_basket_case.mp3',
            modify_date=123456789,
            folder_path='/test/folder'
        )
        db.session.add(test_song)

        db.session.commit()

    response = client.get('/api/songs', query_string={'artist_filter': 'Green', 'song_filter': 'Basket'})
    assert response.status_code == 200
    assert 'songs' in response.get_json()
    songs = response.get_json()['songs']
    assert len(songs) == 1
    assert songs[0]['times_played'] == 1
