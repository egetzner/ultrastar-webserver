import os
import re


def parse_content(lines):
    if lines is not None:
        data = dict()
        is_duet = False
        is_rap = False
        max_beat = 0
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

        players = [line for line in lines if line.startswith('P')]
        data['HasRap'] = is_rap
        data['IsDuet'] = len(players) > 0 | is_duet

    return data


def parse_text_file(text_file):
    encodings = ["utf-8", "iso-8859-1", "ascii"]

    for encoding in encodings:
        try:
            with open(text_file, "r", encoding=encoding) as file:
                lines = file.readlines()
                print(f"is readable for encoding: {encoding}")
                return parse_content(lines)
        except Exception as ex:
            print(ex)
            print("couldn't read file: " + text_file)


def parse_text_file_old(text_file):
    title = None
    artist = None
    language = None
    year = None

    # open file # NOTE: some are ascii, some are utf-8 -> just really depends...
    try:
        with open(text_file, 'r', encoding='iso-8859-1') as txt_file:
            # read lines # TODO: this is really inefficient
            lines = txt_file.readlines()
            # search for metadata (probably in the first 20 lines)
            for line in lines[:20]:
                if line.startswith('#TITLE:'):
                    title = line.replace('#TITLE:', '').strip()
                elif line.startswith('#ARTIST:'):
                    artist = line.replace('#ARTIST:', '').strip()
                elif line.startswith('#LANGUAGE:'):
                    language = line.replace('#LANGUAGE:', '').strip()
                elif line.startswith('#YEAR:'):
                    year = line.replace('#YEAR:', '').strip()
    except Exception as ex:
        print(ex)
        print("couldn't read file: " + text_file)

    return {'Title': title, 'Artist': artist, 'Language': language, 'Year': year}
