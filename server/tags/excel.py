import sqlite3

import pandas as pd


def excel_to_sqlite(excel_path: str, sql_path: str):
    with sqlite3.connect(sql_path) as con:
        df = pd.read_excel(excel_path, sheet_name='Songs', index_col='Folder',
        dtype = {'IsDuet': bool, 'IsRap': bool},
        true_values = [1], false_values = [0])

        df.to_sql('song_info', con, index=True, if_exists='replace')

        con.commit()
