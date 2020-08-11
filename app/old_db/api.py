import pathlib
import sqlite3
import pandas as pd


DB_FILE = pathlib.Path(__file__).resolve().parent.joinpath("weather.db").resolve()


def get_temp_data(table, start, end):
    """
    Query temperature data rows between two ranges

    :params table: name of table
    :params start: start row id
    :params end: end row id
    :returns: pandas dataframe object
    """

    con = sqlite3.connect(str(DB_FILE))
    statement = f'SELECT ID, INSIDE, OUTSIDE, DIF FROM {table} WHERE ID > "{start}" AND ID <= "{end}";'
    df = pd.read_sql_query(statement, con)
    return df


def insert_data(table, id, inside, outside):
    """
    Query temperature data rows between two ranges

    :params table: name of table
    :params id: epoch time
    :params inside: inside temp real
    :params outside: outside temp real
    :returns: pandas dataframe object
    """

    con = sqlite3.connect(str(DB_FILE))
    if table == "TEMPERATURE":
        statement = ''' INSERT INTO TEMPERATURE (ID,INSIDE,OUTSIDE,DIF)
                        VALUES(?,?,?,?) '''
    elif table == "HUMIDITY":
        statement = ''' INSERT INTO HUMIDITY (ID,INSIDE,OUTSIDE,DIF)
                        VALUES(?,?,?,?) '''
    row = (id, inside, outside, outside-inside)
    cur = con.cursor()
    cur.execute(statement, row)
    con.commit()
    return cur.lastrowid
