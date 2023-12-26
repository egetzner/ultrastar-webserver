import os
import re
import glob


def get_songs(song_path):
    os.chdir(song_path)
    files = glob.glob('**/*.txt')
    all_songs = list()
    for file_path in files:
        text_file = os.path.join(song_path, file_path)
        data = parse_text_file(text_file)
        if len(data) > 0:
            data['Folder'] = os.path.dirname(file_path)
            data['FileName'] = os.path.basename(file_path)
            all_songs.append(data)

    return all_songs


def parse_content(lines):
    if lines is not None:
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


def parse_text_file(text_file):
    encodings = ["utf-8", "iso-8859-1", "ascii"]

    for encoding in encodings:
        try:
            with open(text_file, "r", encoding=encoding) as file:
                lines = file.readlines()
                return parse_content(lines)
        except Exception as ex:
            print(ex)
            print("couldn't read file: " + text_file)
