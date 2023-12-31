import os
import re
import glob


def get_filenames(song_path, extension='txt'):
    if not os.path.exists(song_path) or not os.path.isdir(song_path):
        raise Exception(f"not a valid path: '{song_path}'")

    return glob.glob(f'{song_path}/**/*.{extension}')


def parse_content(lines):
    data = dict()
    is_duet = False
    is_rap = False
    max_beat = 0
    players = set()
    for line in lines:

        match = re.search(r'#([\w\d]+):(.*)', line)
        if match:
            data[match.group(1).title()] = match.group(2).strip()
        else:
            match = re.search(r'^.\s(\d+)', line)
            if match:
                beat = int(match.group(1))
                if beat < max_beat:
                    is_duet = True
                max_beat = beat

            if re.search(r'^[R|G]\s', line):
                is_rap = True

            if line.startswith('P'):
                players.add(line.strip())

    data['Players'] = players
    data['HasRap'] = is_rap
    data['IsDuet'] = len(players) > 0 | is_duet
    return data


def parse_text_file(text_file, song_path):
    data = _parse_file_with_unknown_encoding(text_file)
    folder = os.path.dirname(text_file)

    if data is None:
        raise SyntaxError(f"Invalid File: {text_file}")
    else:
        mp3 = data.get('Mp3', '')

        if len(mp3) > 0:
            mp3_path = os.path.join(folder, mp3)
            data['Mp3Path'] = os.path.relpath(mp3_path, start=song_path)

            if not os.path.exists(mp3_path):
                data['Errors'] = "MP3 not found"
        else:
            raise SyntaxError(f"No MP3 found in keys: [{str.join(',', data.keys())}]")

    data['Folder'] = os.path.relpath(folder, start=song_path)
    data['TxtPath'] = os.path.relpath(text_file, start=song_path)
    data['ModifyDate'] = os.path.getmtime(text_file)

    return data


def _parse_file_with_unknown_encoding(text_file):
    encodings = ["utf-8", "iso-8859-1", "ascii"]

    for encoding in encodings:
        try:
            with open(text_file, "r", encoding=encoding) as file:
                lines = file.readlines()
                return parse_content(lines)
        except UnicodeDecodeError:
            pass

    return None
