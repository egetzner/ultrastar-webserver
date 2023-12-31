import os
from flask import Flask, render_template, request, send_file
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from sqlalchemy.orm import class_mapper
from dotenv import load_dotenv, find_dotenv

# make sure to work inside the app context
find_dotenv(raise_error_if_not_found=False)
load_dotenv()

QR_URL = os.getenv('QR_URL')
SONGFOLDER = os.getenv('SONGFOLDER')
SONG_DB = os.getenv('SONG_DB')
ULTRASTAR_DB = os.getenv('ULTRASTAR_DB')


def _create_sqlite_string(connection_string):
    path_with_args = connection_string.removeprefix("sqlite:///")
    path_and_args = path_with_args.split("?")
    path = path_and_args[0]

    args = ''
    if len(path_and_args) > 1:
        args = '?' + '?'.join(path_and_args[1:])

    if os.path.isabs(path) or path == ':memory:':
        abs_path = path
    else:
        abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), path))

    return 'sqlite:///' + abs_path + args


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = _create_sqlite_string(SONG_DB)
app.config['SQLALCHEMY_BINDS'] = {
    'us_db': _create_sqlite_string(ULTRASTAR_DB)
}
db = SQLAlchemy(app)


# Create a class for the songs table
class Song(db.Model):
    __tablename__ = 'songs'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    artist = db.Column(db.String(255))
    album = db.Column(db.String(255))
    genre = db.Column(db.String(255))
    edition = db.Column(db.String(255))
    language = db.Column(db.String(255))
    is_duet = db.Column(db.Boolean)
    year = db.Column(db.Integer)
    mp3_path = db.Column(db.String(255), unique=True)
    modify_date = db.Column(db.Integer)
    folder = db.Column(db.String(255))
    errors = db.Column(db.String(255))


# Create a class for the us_songs table
class USSong(db.Model):
    __bind_key__ = 'us_db'
    __tablename__ = 'us_songs'
    __table_args__ = {'extend_existing': False}
    id = db.Column(db.Integer, primary_key=True)
    artist = db.Column(db.String(255))
    title = db.Column(db.String(255))
    TimesPlayed = db.Column(db.Integer)


def model_to_dict(model):
    """Converts a SQLAlchemy model object to a dictionary."""
    if isinstance(model, list):
        return [model_to_dict(m) for m in model]
    columns = [c.key for c in class_mapper(model.__class__).columns]
    return {c: getattr(model, c) for c in columns}


# Update the handle_song_request function
def handle_song_request(request):
    search_filter = request.args.get('filter')
    artist_filter = request.args.get('artist_filter')
    song_filter = request.args.get('song_filter')
    only_duets = request.args.get('duet_only') == 'true'
    sort_by = request.args.get('sort_by', 'artist')  # Default sort by artist
    limit = request.args.get('limit', 250)  # Default limit to 100 songs
    offset = request.args.get('offset', 0)  # Default offset to 0

    # don't show songs with errors
    query = Song.query.filter(Song.errors.is_(None))

    if search_filter:
        words = search_filter.split(' ')
        for word in words:
            query = query.filter(or_(
                Song.artist.like(f'%{word}%'),
                Song.title.like(f'%{word}%'),
                Song.album.like(f'%{word}%'),
                Song.genre.like(f'%{word}%'),
                Song.edition.like(f'%{word}%')
            ))

    if artist_filter:
        query = query.filter(Song.artist.like(f"%{artist_filter}%"))

    if song_filter:
        query = query.filter(Song.title.like(f"%{song_filter}%"))

    if only_duets:
        query = query.filter(Song.is_duet)

    if sort_by == 'artist':
        query = query.order_by(Song.artist, Song.title)
    elif sort_by == 'title':
        query = query.order_by(Song.title, Song.artist)
    elif sort_by == 'year':
        query = query.order_by(Song.year.desc(), Song.artist, Song.title)
    elif sort_by == 'language':
        query = query.order_by(Song.language.desc(), Song.artist, Song.title)
    elif sort_by == 'genre':
        query = query.order_by(Song.genre, Song.artist, Song.title)
    elif sort_by == 'edition':
        query = query.order_by(Song.edition, Song.artist, Song.title)
    elif sort_by == 'album':
        query = query.order_by(Song.album, Song.artist, Song.title)
    elif sort_by == 'date_added':
        query = query.order_by(Song.modify_date.desc(), Song.artist, Song.title)

    # if querying for times played, don't limit the results
    if sort_by != 'times_played':
        query = query.limit(limit).offset(offset)

    songs = query.all()

    # Retrieve TimesPlayed from us_songs table
    query = USSong.query
    us_songs = query.all()
    us_songs = [model_to_dict(song) for song in us_songs]
    songs = [model_to_dict(song) for song in songs]

    # we have to iterate through all songs because we need to add the times_played field.
    for song in songs:
        match_found = False  # Flag variable to track if a match is found
        for us_song in us_songs:
            if us_song["artist"].rstrip('\x00') == song["artist"] and us_song["title"].rstrip('\x00') == song["title"]:
                song["times_played"] = us_song["TimesPlayed"]
                match_found = True
                break  # Break out of the inner loop
        if not match_found:
            song["times_played"] = 0

    if sort_by == 'times_played':
        # remove songs with 0 times played
        songs = [song for song in songs if song['times_played'] > 0]
        songs = sorted(songs, key=lambda k: (-k['times_played'], k['artist'], k['title']))

        if offset is not None or limit is not None:
            return songs[int(offset):min(int(offset) + int(limit), len(songs))]

    return songs


@app.route('/')
def index():
    songs = handle_song_request(request)
    filter = request.args.get('filter', default='')
    duet_only = request.args.get('duet_only', default='')
    artist_filter = request.args.get('artist_filter', default='')
    song_filter = request.args.get('song_filter', default='')
    sort_by = request.args.get('sort_by', 'artist')  # Default sort by artist
    # get local ip
    return render_template('index.html', songs=songs, filter=filter, artist_filter=artist_filter,
                           song_filter=song_filter,
                           duet_only=duet_only, sort_by=sort_by, local_ip=QR_URL)


@app.route('/api/songs')
def api_songs():
    songs = handle_song_request(request)

    return {'songs': songs}


@app.route('/api/mp3')
def api_mp3():
    # this holds the relative path to the mp3 file
    mp3_path = request.args.get('mp3_path')
    # concat the song path to the song folder
    mp3_path = os.path.join(SONGFOLDER, mp3_path)
    # prevent path traversal
    # return the song from the os
    return send_file(mp3_path, mimetype='audio/mp3')


if __name__ == '__main__':
    print('start')
    app.run(debug=True)
