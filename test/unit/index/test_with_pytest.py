from index import Song, index_songs, session


def test_german_song():
    index_songs()

    result = session.query(Song).filter_by(title="Cruella De Vil").first()

    assert result.artist == "101 Dalmatiner"
    assert (result.language == "German")
    assert (result.year == 1961)
    assert (result.mp3_path == "101 Dalmatiner - Cruella De Vil/101 Dalmatiner - Cruella De Vil.mp3")


def test_english_song():
    index_songs()

    result = session.query(Song).filter_by(artist="10CC").first()

    assert result.title == "I'm Not In Love"
    assert result.artist == "10CC"
    assert (result.language == "English")
    assert (result.year == 1975)
    assert (result.mp3_path == "10CC - I'm Not In Love/10CC - I'm Not In Love.mp3")
