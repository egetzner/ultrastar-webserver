import os
import pytest
from server.parser import parse_text_file, get_filenames

SONG_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/songs"))


def _parse_file(short_path):
    filepath = os.path.join(SONG_FOLDER, short_path)
    return parse_text_file(filepath, SONG_FOLDER)


@pytest.mark.parametrize("test_input, extension, files",
                         [("/", "txt", 9),
                          ("/", "mp3", 6),
                          ("", 'txt', 9),
                          ("", "mp3", 6)])
def test_get_filenames(test_input, extension, files):
    names = get_filenames(SONG_FOLDER + test_input, extension)

    assert len(names) == files


@pytest.mark.parametrize("path", ["invalid/path/not/found", "../db/Ultrastar.db"])
def test_get_filenames_invalid_path(path):
    with pytest.raises(Exception):
        get_filenames(os.path.join(SONG_FOLDER + path))


def test_read_missing_mp3_file():
    result = _parse_file("Crazy Ex-Girlfriend - You Stupid Bitch/Crazy Ex-Girlfriend - You Stupid Bitch.txt")

    assert result['Title'] == "You Stupid Bitch"
    assert result['Artist'] == "Crazy Ex-Girlfriend"
    assert result['Folder'] == "Crazy Ex-Girlfriend - You Stupid Bitch"
    assert result['Mp3Path'] == "Crazy Ex-Girlfriend - You Stupid Bitch/Crazy Ex-Girlfriend - You Stupid Bitch.mp3"
    assert result['TxtPath'] == "Crazy Ex-Girlfriend - You Stupid Bitch/Crazy Ex-Girlfriend - You Stupid Bitch.txt"
    assert result['Errors'] == "MP3 not found"


def test_read_invalid_text_file():
    with pytest.raises(SyntaxError):
        _parse_file("Ricky Martin - La vida loca/Ricky Marin - La Vida Loca.txt")


@pytest.mark.parametrize("test_input,expected",
                         [("101 Dalmatiner - Cruella De Vil/101 Dalmatiner - Cruella De Vil.txt", "Cruella De Vil"),
                          ("10CC - I'm Not In Love/10CC - I'm Not In Love.txt", "I'm Not In Love")])
def test_read_single_file(test_input, expected):
    result = _parse_file(test_input)

    assert 'Title' in result
    assert result['Title'] == expected
    assert result['Folder'] == os.path.dirname(test_input)
    assert result['TxtPath'] == test_input
    assert result['Mp3Path'] == test_input.replace(".txt", ".mp3")


def test_read_all_fields():
    short_path = "Ariana Grande & John Legend - Beauty and the Beast" \
                 "/Ariana Grande & John Legend - Beauty and the Beast.txt"

    result = _parse_file(short_path)

    assert result['Title'] == "Beauty and the Beast"
    assert result['Artist'] == "Ariana Grande & John Legend"
    assert result['Album'] == "Beauty and the Beast"
    assert result['Language'] == "English"
    assert result['Edition'] == "Disney"
    assert result['Genre'] == "Musical"
    assert result['Year'] == "2017"

    assert result['Folder'] == "Ariana Grande & John Legend - Beauty and the Beast"
    assert result['TxtPath'] == short_path
    assert result['Mp3Path'] == "Ariana Grande & John Legend - Beauty and the Beast" \
                                "/Ariana Grande & John Legend - Beauty and the Beast.mp3"

    assert not result['HasRap']
    assert not result['IsDuet']


def test_read_all_fields_duet():
    short_path = "Ariana Grande & John Legend - Beauty and the Beast" \
                 "/Ariana Grande & John Legend - Beauty and the Beast [MULTI].txt"

    result = _parse_file(short_path)

    assert result['Title'] == "Beauty and the Beast (Pop Version)"
    assert result['Artist'] == "Ariana Grande & John Legend"
    assert result['Album'] == "Beauty and the Beast"
    assert result['Language'] == "English"
    assert result['Edition'] == "Disney"
    assert result['Genre'] == "Musical"
    assert result['Year'] == "2017"
    assert result['TxtPath'] == short_path

    assert result['Players'] == {"P 1", "P 2"}
    assert not result['HasRap']
    assert result['IsDuet']


def test_read_all_fields_duet_freestyle():
    short_path = "Hamilton Broadway Cast - Cabinet Battle #1/Hamilton Broadway Cast - Cabinet Battle #1.txt"

    result = _parse_file(short_path)

    assert result['Title'] == "Cabinet Battle #1"
    assert result['Artist'] == "Hamilton"
    assert result['Album'] == "Hamilton"
    assert result['Language'] == "English"
    assert result['Edition'] == "Musicals"
    assert result['Genre'] == "Musical"
    assert result['Year'] == "2015"
    assert result['TxtPath'] == short_path

    assert result['Players'] == {"P 1", "P 2"}
    assert not result['HasRap']  # because it is freestyle
    assert result['IsDuet']


def test_read_all_fields_rap():
    short_path = "Eminem - Lose yourself/Eminem - Lose yourself.txt"

    result = _parse_file(short_path)

    assert result['Title'] == "Lose yourself"
    assert result['Artist'] == "Eminem"
    assert result['Language'] == "English"
    assert result['Genre'] == "Rap"
    assert result['Year'] == "2002"
    assert result['TxtPath'] == short_path

    assert result['Players'] == set()
    assert result['HasRap']
    assert not result['IsDuet']
