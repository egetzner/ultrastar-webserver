from repository import Song
from index import session

# NOTE: this will expect the .env file, instead of the setup .test.env file, because it imports from index directly.


def test_german_song():

    result = session.query(Song).filter_by(title="Cruella De Vil").first()

    assert result.artist == "101 Dalmatiner"
    assert (result.language == "German")
    assert (result.year == 1961)
    assert (result.folder_path == "101 Dalmatiner - Cruella De Vil")
    assert (result.cover_path == "101 Dalmatiner - Cruella De Vil.jpg")
    assert (result.mp3_path == "101 Dalmatiner - Cruella De Vil/101 Dalmatiner - Cruella De Vil.mp3")


def test_english_song():

    result = session.query(Song).filter_by(artist="10CC").first()

    assert result.title == "I'm Not In Love"
    assert result.artist == "10CC"
    assert (result.language == "English")
    assert (result.year == 1975)
    assert (result.folder_path == "10CC - I'm Not In Love")
    assert (result.cover_path == "10CC - I'm Not In Love.jpg")
    assert (result.mp3_path == "10CC - I'm Not In Love/10CC - I'm Not In Love.mp3")


def test_duet():

    result = session.query(Song).filter_by(is_duet=True).first()

    assert result.title.startswith("Beauty and the Beast")


def test_rap():

    result = session.query(Song).filter_by(is_rap=True).first()

    assert result.title == "Lose yourself"


def test_cover():

    result = session.query(Song).filter_by(album='Hamilton').first()

    assert result.title == "Cabinet Battle #1"
    assert (result.folder_path == "Hamilton Broadway Cast - Cabinet Battle #1")
    assert (result.cover_path == "Hamilton Broadway Cast - Cabinet Battle #1 [CO].jpg")
    assert (result.mp3_path == "Hamilton Broadway Cast - Cabinet Battle #1"
                               "/Hamilton Broadway Cast - Cabinet Battle #1.mp3")
