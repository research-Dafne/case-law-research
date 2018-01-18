import sqlite3

CONN_STRING = '/media/sf_VBox_Shared/CaseLaw/caselaw.db'


def get_connection():
    conn = sqlite3.connect(CONN_STRING)
    return conn