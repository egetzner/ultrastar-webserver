import os
import pytest
from parser import parse_text_file, get_songs
from dotenv import load_dotenv

load_dotenv()
SONGFOLDER = os.getenv('SONGFOLDER')


def _parse_file(short_path):
    filepath = os.path.join(SONGFOLDER, short_path)
    return parse_text_file(filepath)


@pytest.mark.parametrize("test_input,expected",
                         [("101 Dalmatiner - Cruella De Vil/101 Dalmatiner - Cruella De Vil.txt", "Cruella De Vil"),
                          ("10CC - I'm Not In Love/10CC - I'm Not In Love.txt", "I'm Not In Love")])
def test_read_single_file(test_input, expected):
    result = _parse_file(test_input)

    assert 'Title' in result
    assert result['Title'] == expected


def test_read_all_fields():
    short_path = "Ariana Grande & John Legend - Beauty and the Beast/Ariana Grande & John Legend - Beauty and the Beast.txt"

    result = _parse_file(short_path)

    assert result['Title'] == "Beauty and the Beast"
    assert result['Artist'] == "Ariana Grande & John Legend"
    assert result['Album'] == "Beauty and the Beast"
    assert result['Language'] == "English"
    assert result['Edition'] == "Disney"
    assert result['Genre'] == "Musical"
    assert result['Year'] == "2017"

    assert not result['HasRap']
    assert not result['IsDuet']


def test_read_all_fields_duet():
    short_path = "Ariana Grande & John Legend - Beauty and the Beast/Ariana Grande & John Legend - Beauty and the Beast [MULTI].txt"

    result = _parse_file(short_path)

    assert result['Title'] == "Beauty and the Beast (Pop Version)"
    assert result['Artist'] == "Ariana Grande & John Legend"
    assert result['Album'] == "Beauty and the Beast"
    assert result['Language'] == "English"
    assert result['Edition'] == "Disney"
    assert result['Genre'] == "Musical"
    assert result['Year'] == "2017"

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

    assert result['Players'] == set()
    assert result['HasRap']
    assert not result['IsDuet']
