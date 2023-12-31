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

    with app.app_context():
        db.metadata.reflect(bind=db.engine)
        db.metadata.tables[Song.__tablename__].drop(bind=db.engine)


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
            folder='Eminem - Lose yourself'
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
            folder='/test/folder'
        )
        db.session.add(test_song)

        db.session.commit()

    response = client.get('/api/songs', query_string={'artist_filter': 'Green', 'song_filter': 'Basket'})
    assert response.status_code == 200
    assert 'songs' in response.get_json()
    songs = response.get_json()['songs']
    assert len(songs) == 1
    assert songs[0]['times_played'] == 1


def test_handle_song_request_duet_only(client):
    # Add necessary test data to the database
    with app.app_context():
        test_song = Song(
            title='Basket Case',
            artist='Green Day',
            language='English',
            is_duet=False,
            year=2022,
            mp3_path='green_day_basket_case.mp3',
            modify_date=123456789,
            folder='/test/folder'
        )
        db.session.add(test_song)

        duet_song = Song(
            title='Tribute',
            artist='Tenacious D',
            language='English',
            is_duet=True,
            year=2022,
            mp3_path='tenacious_d.mp3',
            modify_date=123456789,
            folder='/test/folder'
        )
        db.session.add(duet_song)

        db.session.commit()

    response = client.get('/api/songs', query_string={'duet_only': 'true'})
    assert response.status_code == 200
    assert 'songs' in response.get_json()
    songs = response.get_json()['songs']
    assert len(songs) == 1
    assert songs[0]['title'] == 'Tribute'


@pytest.mark.parametrize("filter,expected",
                         [('Green', ['Basket Case']),
                          ('Basket', ['Basket Case']),
                          ('Green Basket ', ['Basket Case']),
                          (' tenacious ', ['Tribute']),
                          (' toto ', ['Africa'])])
def test_handle_song_request_search_filter(client, filter, expected):
    # Add necessary test data to the database
    with app.app_context():
        test_song = Song(
            title='Basket Case',
            artist='Green Day',
            language='English',
            year=2022,
            mp3_path='green_day_basket_case.mp3',
            modify_date=123456789,
            folder='/test/folder'
        )
        second_song = Song(
            title='Tribute',
            artist='Tenacious D',
            language='English',
            year=2022,
            mp3_path='tenacious_d.mp3',
            modify_date=123456789,
            folder='/test/folder'
        )

        third_song = Song(
            title='Africa',
            artist='Toto',
            language='English',
            year=2022,
            mp3_path='africa.mp3',
            modify_date=123456789,
            folder='/test/folder'
        )
        db.session.add(test_song)
        db.session.add(second_song)
        db.session.add(third_song)

        db.session.commit()

    response = client.get('/api/songs', query_string={'filter': filter})
    assert response.status_code == 200
    assert 'songs' in response.get_json()
    songs = response.get_json()['songs']
    assert [song['title'] for song in songs] == expected


@pytest.mark.parametrize("limit,offset,expected",
                         [('1','0',1),
                          (2,0,2),
                          (3,0,3),
                          (1,1,1),
                          ('1','3',0)])
def test_handle_song_request_with_times_play_sorted(client, limit, offset, expected):
    # Add necessary test data to the database
    with app.app_context():
        test_song = Song(
            title='Basket Case',
            artist='Green Day',
            language='English',
            year=2022,
            mp3_path='green_day_basket_case.mp3',
            modify_date=123456789,
            folder='/test/folder'
        )
        second_song = Song(
            title='Tribute',
            artist='Tenacious D',
            language='English',
            year=2022,
            mp3_path='tenacious_d.mp3',
            modify_date=123456789,
            folder='/test/folder'
        )

        third_song = Song(
            title='Africa',
            artist='Toto',
            language='English',
            year=2022,
            mp3_path='africa.mp3',
            modify_date=123456789,
            folder='/test/folder'
        )
        db.session.add(test_song)
        db.session.add(second_song)
        db.session.add(third_song)

        db.session.commit()

    response = client.get('/api/songs', query_string={'sort_by': 'times_played', 'limit': limit, 'offset': offset})
    assert response.status_code == 200
    assert 'songs' in response.get_json()
    songs = response.get_json()['songs']
    assert len(songs) == expected

    if offset == 0:
        assert songs[0]['artist'] == 'Green Day'
        assert songs[0]['times_played'] == 1
    elif offset == 1:
        assert songs[0]['artist'] == 'Tenacious D'
        assert songs[0]['times_played'] == 1

    if expected > 1:
        assert songs[1]['artist'] == 'Tenacious D'
        assert songs[1]['times_played'] == 1


@pytest.mark.parametrize("sort_by,expected",
                         [('title', ['Basket Case', 'Hello', 'Tribute']),
                          ('artist', ['Hello', 'Basket Case', 'Tribute']),
                          ('year', ['Hello', 'Tribute', 'Basket Case']),
                          ('language', ['Tribute', 'Hello', 'Basket Case']),
                          ('times_played', ['Basket Case', 'Tribute']),
                          ('date_added', ['Tribute', 'Hello', 'Basket Case']),
                          ('album', ['Basket Case', 'Tribute', 'Hello']),
                          ('genre', ['Basket Case', 'Tribute', 'Hello']),
                          ('edition', ['Basket Case', 'Tribute', 'Hello']),
                          ])
def test_handle_song_request_sort(client, sort_by, expected):
    # Add necessary test data to the database
    with app.app_context():
        test_song = Song(
            title='Basket Case',
            artist='Green Day',
            language='English',
            year=2002,
            mp3_path='green_day_basket_case.mp3',
            modify_date=11111,
            folder='/test/folder'
        )
        second_song = Song(
            title='Tribute',
            artist='Tenacious D',
            language='German',
            year=2010,
            mp3_path='tenacious_d.mp3',
            modify_date=33333,
            folder='/test/folder'
        )

        third_song = Song(
            title='Hello',
            artist='Adele',
            album='Rumours',
            genre='Pop',
            edition='SingStar',
            language='English',
            year=2015,
            mp3_path='adele.mp3',
            modify_date=22222,
            folder='/test/folder'
        )
        db.session.add(test_song)
        db.session.add(second_song)
        db.session.add(third_song)

        db.session.commit()

    response = client.get('/api/songs', query_string={'sort_by': sort_by})
    assert response.status_code == 200
    assert 'songs' in response.get_json()
    songs = response.get_json()['songs']
    assert [song['title'] for song in songs] == expected
