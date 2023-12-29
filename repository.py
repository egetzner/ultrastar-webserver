from parser import parse_text_file
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

# Create a base class for declarative models
Base = declarative_base()


class Song(Base):
    __tablename__ = 'songs'
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    artist = Column(String(255))
    album = Column(String(255))
    genre = Column(String(255))
    edition = Column(String(255))
    language = Column(String(255))
    year = Column(Integer)
    is_rap = Column(Boolean)
    is_duet = Column(Boolean)
    mp3_path = Column(String(255), unique=True)
    cover_path = Column(String(255))
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
                            album=data.get('Album'),genre=data.get('Genre'),edition=data.get('Edition'),
                            is_rap=data.get('HasRap', False), is_duet=data.get('IsDuet', False),
                            mp3_path=data.get('Mp3Path'),modify_date=data.get('ModifyDate'),
                            cover_path=data.get('Cover'),folder_path=data.get('Folder'))

                # depending on what we find to be the "unique key" - currently it's the mp3 file
                existing_song = self.session.query(Song).filter_by(mp3_path=data['Mp3Path']).first()

                if existing_song:
                    edited += 1
                    if song.title is not None:
                        existing_song.title = song.title

                    if song.artist is not None:
                        existing_song.artist = song.artist

                    if song.album is not None:
                        existing_song.album = song.album

                    if song.genre is not None:
                        existing_song.genre = song.genre

                    if song.edition is not None:
                        existing_song.edition = song.edition

                    if song.language is not None:
                        existing_song.language = song.language

                    if song.year is not None:
                        existing_song.year = song.year

                    existing_song.is_rap |= song.is_rap
                    existing_song.is_duet |= song.is_duet

                    if song.modify_date is not None:
                        existing_song.modify_date = song.modify_date

                    if song.cover_path is not None:
                        existing_song.cover_path = song.cover_path

                    if song.folder_path is not None:
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
