import os
import pytest
from app import app, db, Song, USSong


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_BINDS'] = {}
    client = app.test_client()

    with app.app_context():
        db.create_all()

    yield client

    with app.app_context():
        db.drop_all()


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
            title='Test Song',
            artist='Test Artist',
            language='English',
            year=2022,
            mp3_path='test.mp3',
            modify_date=123456789,
            folder_path='test/data/songs/'
        )
        db.session.add(test_song)
        db.session.commit()

    response = client.get('/api/mp3', query_string={'mp3_path': 'test.mp3'})
    assert response.status_code == 200
    assert response.content_type == 'audio/mp3'


def test_handle_song_request(client):
    # Add necessary test data to the database
    with app.app_context():
        test_song = Song(
            title='Test Song',
            artist='Test Artist',
            language='English',
            year=2022,
            mp3_path='test.mp3',
            modify_date=123456789,
            folder_path='/test/folder'
        )
        db.session.add(test_song)

        test_us_song = USSong(
            artist='Test Artist',
            title='Test Song',
            TimesPlayed=5
        )
        db.session.add(test_us_song)

        db.session.commit()

    response = client.get('/api/songs', query_string={'artist_filter': 'Test', 'song_filter': 'Song'})
    assert response.status_code == 200
    assert 'songs' in response.get_json()
    songs = response.get_json()['songs']
    assert len(songs) == 1
    assert songs[0]['times_played'] == 5
