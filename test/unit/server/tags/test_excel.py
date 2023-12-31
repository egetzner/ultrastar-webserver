import os
from server.tags.excel import excel_to_sqlite

EXCEL_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/db/song_info_2020-08-11.xlsx"))
INFO_DB = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/db/test.db"))


def test_excel_read_in():
    excel_to_sqlite(EXCEL_FILE, INFO_DB)
