import os

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from dotenv import load_dotenv, find_dotenv
from parser import get_filenames
from repository import SongIndexer, Base

find_dotenv(raise_error_if_not_found=True)
load_dotenv()


path_to_file = os.path.abspath(__file__)
SONG_FOLDER = os.getenv('SONGFOLDER')

SONG_DB = os.getenv('SONG_DB')

# Configure the SQLAlchemy engine
engine = create_engine(SONG_DB)

# Create a session factory
Session = sessionmaker(bind=engine)

session = Session()

# Create or update songs in the database
all_songs = get_filenames(SONG_FOLDER, 'txt')

# Create the database tables
Base.metadata.create_all(engine)

indexer = SongIndexer(session)
indexer.index_songs(all_songs, SONG_FOLDER)