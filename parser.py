import os
import re
import glob


def get_filenames(song_path, extension='txt'):
    if not os.path.exists(song_path):
        raise Exception(f"not a valid path: '{song_path}'")

    if os.path.isdir(song_path):
        directory = song_path
    else:
        directory = os.path.dirname(song_path)
    return glob.glob(directory + '/**/*.' + extension)


def parse_content(lines):
    if not lines:
        return None

    data = dict()
    is_duet = False
    is_rap = False
    max_beat = 0
    players = set()
    for line in lines:

        match = re.search('#([\w\d]+):(.*)', line)
        if match:
            data[match.group(1).title()] = match.group(2).strip()
        else:
            match = re.search('^.\s(\d+)', line)
            if match:
                beat = int(match.group(1))
                if beat < max_beat:
                    is_duet = True
                max_beat = beat

            if re.search('^[R|G]\s', line):
                is_rap = True

            if line.startswith('P'):
                players.add(line.strip())

    data['Players'] = players
    data['HasRap'] = is_rap
    data['IsDuet'] = len(players) > 0 | is_duet
    return data


def parse_text_file(text_file, song_path):
    data = _parse_file_with_unknown_encoding(text_file)
    if data is not None and len(data) > 0:

        folder = os.path.dirname(text_file)
        mp3_path = os.path.join(folder, data['Mp3'])

        if not os.path.exists(mp3_path):
            print(f"Warning: MP3 Not found: {mp3_path}")
            return None

        data['FileName'] = os.path.basename(text_file)
        data['Folder'] = os.path.relpath(folder, start=song_path)
        data['Mp3Path'] = os.path.relpath(mp3_path, start=song_path)
        data['ModifyDate'] = os.path.getmtime(folder)

        return data

    return None


def _parse_file_with_unknown_encoding(text_file):
    encodings = ["utf-8", "iso-8859-1", "ascii"]

    for encoding in encodings:
        try:
            with open(text_file, "r", encoding=encoding) as file:
                lines = file.readlines()
                return parse_content(lines)
        except Exception as ex:
            print(ex)
            print("couldn't read file: " + text_file)
