import os

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from dotenv import load_dotenv
from parser import get_songs

load_dotenv()
SONGFOLDER = os.getenv('SONGFOLDER')
SONG_DB = os.getenv('SONG_DB')

# Configure the SQLAlchemy engine
engine = create_engine(SONG_DB)

# Create a session factory
Session = sessionmaker(bind=engine)

# Create a base class for declarative models
Base = declarative_base()

# Create the database tables
Base.metadata.create_all(engine)


class Song(Base):
    __tablename__ = 'songs'
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    artist = Column(String(255))
    language = Column(String(255))
    year = Column(Integer)
    mp3_path = Column(String(255), unique=True)
    modify_date = Column(Integer)
    folder_path = Column(String(255))


# Create a session
session = Session()


def index_songs():
    # Create db
    Base.metadata.create_all(engine)
    batch = 500
    count = 0
    edited = 0
    added = 0

    all_songs = get_songs(SONGFOLDER)

    for i in range(0, len(all_songs), batch):
        for song_data in all_songs[i:i + batch]:
            folder = song_data['Folder']
            mp3 = song_data['Mp3']
            mp3_path = os.path.join(folder, mp3)

            title = song_data['Title']
            artist = song_data['Artist']
            language = song_data['Language']
            year = song_data['Year']

            # check if song is already in database
            # get modify date of folder
            # this is the date the song was added to the database
            modify_date = os.path.getmtime(folder)

            # create song object
            song = Song(title=title, artist=artist, language=language, year=year, mp3_path=mp3_path,
                        folder_path=folder, modify_date=modify_date)

            if session.query(Song).filter_by(mp3_path=mp3_path).first():
                # update song in database
                edited += 1
                session.query(Song).filter_by(mp3_path=mp3_path).update(
                    {'title': title, 'artist': artist, 'language': language, 'year': year, 'modify_date': modify_date,
                     'folder_path': song.folder_path})
            else:
                # add to database
                session.add(song)
                added += 1
            count += 1
        print(f"processed {count} songs...")
        session.commit()

    session.commit()
    print(f"processed {count} songs in total.")
    print(f"added {added} songs.")
    print(f"edited {edited} songs.")
    print("done.")


index_songs()
