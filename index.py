import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from dotenv import load_dotenv, find_dotenv
from server.parser import get_filenames
from server.repository import SongIndexer, Base


class SongProcessor:
    def __init__(self, song_folder, song_db):
        self.song_folder = song_folder
        self.song_db = song_db

        # Configure the SQLAlchemy engine
        self.engine = create_engine(self.song_db)

        # Create a session factory
        self.session_factory = sessionmaker(bind=self.engine)

    def process_songs(self, tag_db=None):
        with self.session_factory() as session:

            # Create or update songs in the database
            all_songs = get_filenames(self.song_folder, 'txt')

            print(f'Found {len(all_songs)} files to parse...')

            # Create the database tables
            Base.metadata.create_all(self.engine)

            if tag_db and os.path.exists(tag_db):
                self.attach_tags(tag_db)

            indexer = SongIndexer(session)
            indexer.index_songs(all_songs, self.song_folder)

    def attach_tags(self, tag_path):
        with self.session_factory() as session:
            session.execute(f"ATTACH DATABASE '{tag_path}' AS tags;")
            session.execute("INSERT OR REPLACE INTO song_info SELECT * FROM tags.song_info ;")
            session.commit()


# Usage
if __name__ == "__main__":
    find_dotenv(raise_error_if_not_found=True)
    load_dotenv()

    SONG_FOLDER = os.getenv('SONGFOLDER')
    SONG_DB = os.getenv('SONG_DB')
    TAG_DB = os.getenv('TAG_DB')

    print(f'Looking for Songs in {SONG_FOLDER}')
    print(f'Writing songs to {SONG_DB}')
    print(f'Getting tags from {TAG_DB}')

    processor = SongProcessor(SONG_FOLDER, SONG_DB)
    processor.process_songs()
    processor.attach_tags(TAG_DB)
