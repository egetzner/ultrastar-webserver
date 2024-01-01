import os

import pytest

from server.repository import Song, SongVersion, SongInfo
from index import SongProcessor

SONG_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/songs"))
TAG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/tags.db'))

OUTPUT_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data'))
SONG_DB = os.path.join(OUTPUT_FOLDER, "output.db")


@pytest.fixture
def session():
    processor = SongProcessor(SONG_FOLDER, f'sqlite:///{SONG_DB}')
    processor.process_songs(tag_db=TAG_PATH)
    return processor.session_factory()

def test_german_song(session):
    result = session.query(Song).filter_by(title="Cruella De Vil").first()

    assert result.artist == "101 Dalmatiner"
    assert (result.language == "German")
    assert (result.year == 1961)
    assert (result.folder == "101 Dalmatiner - Cruella De Vil")
    assert (result.cover_path == "101 Dalmatiner - Cruella De Vil.jpg")
    assert (result.mp3_path == "101 Dalmatiner - Cruella De Vil/101 Dalmatiner - Cruella De Vil.mp3")


def test_english_song(session):
    result = session.query(Song).filter_by(artist="10CC").first()

    assert result.title == "I'm Not In Love"
    assert result.artist == "10CC"
    assert (result.language == "English")
    assert (result.year == 1975)
    assert (result.folder == "10CC - I'm Not In Love")
    assert (result.cover_path == "10CC - I'm Not In Love.jpg")
    assert (result.mp3_path == "10CC - I'm Not In Love/10CC - I'm Not In Love.mp3")


def test_duet(session):
    song = session.query(Song).filter_by(is_duet=True).first()
    versions = session.query(SongVersion).filter_by(folder='Ariana Grande & John Legend - Beauty and the Beast').all()
    info = session.query(SongInfo).filter_by(folder='Ariana Grande & John Legend - Beauty and the Beast').all()

    assert song.title.startswith("Beauty and the Beast")
    assert len(versions) == 2
    assert len(info) == 1

    assert info[0].title == "Beauty and the Beast"
    assert info[0].category == "Disney"
    assert info[0].movie == "Beauty and the Beast (2017)"
    assert info[0].ost == "Beauty and the Beast"


def test_rap(session):
    result = session.query(Song).filter_by(is_rap=True).first()
    info = session.query(SongInfo).filter_by(folder='Eminem - Lose yourself').all()

    assert len(info) == 1

    assert result.title == "Lose yourself"
    assert info[0].title == "Lose yourself"
    assert info[0].ost == "8 Mile"
    assert info[0].interests == "Elisabeth,Theo"


def test_cover(session):
    result = session.query(Song).filter_by(album='Hamilton').first()

    assert result.title == "Cabinet Battle #1"
    assert (result.folder == "Hamilton Broadway Cast - Cabinet Battle #1")
    assert (result.cover_path == "Hamilton Broadway Cast - Cabinet Battle #1 [CO].jpg")
    assert (result.mp3_path == "Hamilton Broadway Cast - Cabinet Battle #1"
                               "/Hamilton Broadway Cast - Cabinet Battle #1.mp3")
