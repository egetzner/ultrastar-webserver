import os
import unittest
from index import Song, index_songs, session

from dotenv import load_dotenv

class TestDatabaseReadIn(unittest.TestCase):

    def test_german_song(self):
        index_songs()

        result = session.query(Song).filter_by(title="Cruella De Vil").first()

        self.assertEqual(result.artist, "101 Dalmatiner")
        self.assertEqual(result.language, "German")
        self.assertEqual(result.year, 1961)
        self.assertEqual(result.mp3_path, "101 Dalmatiner - Cruella De Vil/101 Dalmatiner - Cruella De Vil.mp3")

    def test_english_song(self):
        index_songs()

        result = session.query(Song).filter_by(artist="10CC").first()

        self.assertEqual(result.title, "I'm Not In Love")
        self.assertEqual(result.artist, "10CC")
        self.assertEqual(result.language, "English")
        self.assertEqual(result.year, 1975)
        self.assertEqual(result.mp3_path, "10CC - I'm Not In Love/10CC - I'm Not In Love.mp3")


if __name__ == '__main__':
    unittest.main()
