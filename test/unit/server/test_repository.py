import pytest
from unittest.mock import patch
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from server.repository import Song, SongIndexer, Base

# Use SQLite in-memory database for testing
DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="module")
def engine():
    return create_engine(DATABASE_URL, echo=True)


@pytest.fixture
def db_session(engine):
    Base.metadata.create_all(bind=engine)
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def mock_parse_text_file():
    with patch('server.repository.parse_text_file') as mock_parse:
        yield mock_parse


def test_index_songs_added(db_session, mock_parse_text_file):
    # Mock data for testing
    mock_files = [
        'file1.txt',
        'file2.txt',
        # Add more mock files as needed
    ]

    mock_parse_text_file.side_effect = [{
        'Title': 'Song 1',
        'Artist': 'Artist 1',
        'Language': 'English',
        'Year': 2022,
        'Mp3Path': '/path/to/song1.mp3',
        'ModifyDate': 1234567890,
        'Folder': '/path/to/folder1'
    }, {
        'Title': 'Song 2',
        'Artist': 'Artist 2',
        'Language': 'English',
        'Album': 'Album',
        'Genre': 'My Genre',
        'Edition': 'SingStar',
        'IsDuet': True,
        'HasRap': True,
        'Year': 2022,
        'Mp3Path': '/path/to/song2.mp3',
        'ModifyDate': 1234567890,
        'Folder': '/path/to/folder2',
        'Errors': 'test errors'
    }]

    # Create an instance of the SongIndexer with the in-memory database session
    indexer = SongIndexer(session=db_session)

    # Call the index_songs method with mock data
    indexer.index_songs(mock_files, 'test')

    # Assert that the session's add method was called for each added song
    added_songs = db_session.query(Song).all()

    assert len(added_songs) == len(mock_files)

    assert added_songs[0].title == 'Song 1'
    assert added_songs[0].artist == 'Artist 1'
    assert not added_songs[0].is_duet
    assert not added_songs[0].is_rap

    assert added_songs[1].title == 'Song 2'
    assert added_songs[1].artist == 'Artist 2'
    assert added_songs[1].language == 'English'
    assert added_songs[1].album == 'Album'
    assert added_songs[1].genre == 'My Genre'
    assert added_songs[1].edition == 'SingStar'
    assert added_songs[1].is_duet
    assert added_songs[1].is_rap
    assert added_songs[1].year == 2022
    assert added_songs[1].mp3_path == '/path/to/song2.mp3'
    assert added_songs[1].folder_path == '/path/to/folder2'
    assert added_songs[1].errors == 'test errors'


def test_index_songs_edited(db_session, mock_parse_text_file):
    # Mock data for testing
    mock_files = [
        'file3.txt',  # This file will simulate an edited song
        # Add more mock files as needed
    ]

    mock_parse_text_file.return_value = {
        'Title': 'Song 2',
        'Artist': 'Artist 2',
        'Language': 'English',
        'Album': 'Album',
        'Genre': 'My Genre',
        'Edition': 'SingStar',
        'IsDuet': True,
        'HasRap': True,
        'Year': 2023,
        'Mp3Path': '/path/to/song2.mp3',
        'ModifyDate': 1234567890,
        'Folder': '/path/to/folder2'
    }

    # already added the second song
    existing_song = Song(mp3_path='/path/to/song2.mp3', is_duet=False, is_rap=False)
    db_session.add(existing_song)
    db_session.commit()

    # Create an instance of the SongIndexer with the in-memory database session
    indexer = SongIndexer(session=db_session)

    # Call the index_songs method with mock data
    indexer.index_songs(mock_files, 'test')

    # Assert that the session's query and update methods were called for each edited song
    assert db_session.query(Song).count() == len(mock_files)

    updated_song = db_session.query(Song).first()

    assert updated_song.title == 'Song 2'
    assert updated_song.artist == 'Artist 2'
    assert updated_song.language == 'English'
    assert updated_song.year == 2023
    assert updated_song.modify_date == 1234567890
    assert updated_song.folder_path == '/path/to/folder2'
    assert updated_song.album == 'Album'
    assert updated_song.edition == 'SingStar'
    assert updated_song.genre == 'My Genre'
    assert updated_song.is_rap
    assert updated_song.is_duet


def test_edit_duet_song(db_session, mock_parse_text_file):
    # Mock data for testing
    mock_files = [
        'file4.txt',  # This file will simulate an edited song
        # Add more mock files as needed
    ]

    key = '/path/to/song2.mp3'

    mock_parse_text_file.return_value = {
        'Title': 'Song 2',
        'Artist': 'Artist 2',
        'Language': 'English',
        'Album': 'Album',
        'Genre': 'My Genre',
        'Edition': 'SingStar',
        'IsDuet': False,
        'IsRap': False,
        'Year': 2023,
        'Mp3Path': key,
        'ModifyDate': 1234567890,
        'Folder': '/path/to/folder2'
    }

    # already added the second song
    existing_song = Song(mp3_path=key, title='Original Title', is_duet=True, is_rap=True)
    db_session.add(existing_song)
    db_session.commit()

    # Create an instance of the SongIndexer with the in-memory database session
    indexer = SongIndexer(session=db_session)

    # Call the index_songs method with mock data
    indexer.index_songs(mock_files, 'test')

    # Assert that the session's query and update methods were called for each edited song
    assert db_session.query(Song).count() == len(mock_files)

    updated_song = db_session.query(Song).first()

    assert updated_song.title == 'Song 2'
    assert updated_song.artist == 'Artist 2'
    assert updated_song.year == 2023
    assert updated_song.modify_date == 1234567890
    assert updated_song.folder_path == '/path/to/folder2'
    assert updated_song.album == 'Album'
    assert updated_song.edition == 'SingStar'
    assert updated_song.genre == 'My Genre'
    assert updated_song.is_rap
    assert updated_song.is_duet
