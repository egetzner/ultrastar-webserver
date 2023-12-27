from parser import parse_text_file
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# Create a base class for declarative models
Base = declarative_base()


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


class SongIndexer:
    def __init__(self, session, batch_size=250):
        self.session = session
        self.batch_size = batch_size

    def index_songs(self, all_songs, song_folder):

        count = 0
        edited = 0
        added = 0

        for i in range(0, len(all_songs), self.batch_size):
            for file in all_songs[i:i + self.batch_size]:

                data = parse_text_file(file, song_folder)

                if data is None:
                    break

                song = Song(title=data.get('Title'),artist=data.get('Artist'),
                            language=data.get('Language'),year=data.get('Year'),
                            mp3_path=data.get('Mp3Path'),modify_date=data.get('ModifyDate'),
                            folder_path=data.get('Folder'))

                #depending on what we find to be the "unique key" - currently it's the mp3 file
                existing_song = self.session.query(Song).filter_by(mp3_path=data['Mp3Path']).first()

                if existing_song:
                    edited += 1
                    existing_song.title = song.title
                    existing_song.artist = song.artist
                    existing_song.language = song.language
                    existing_song.year = song.year
                    existing_song.modify_date = song.modify_date
                    existing_song.folder_path = song.folder_path
                else:
                    added += 1
                    self.session.add(song)

                count += 1

            self.session.commit()

        print(f"Processed {count} songs in total.")
        print(f"Added {added} songs.")
        print(f"Edited {edited} songs.")
        print("Done.")
