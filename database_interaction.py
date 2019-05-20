import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)


def insert_flight(conn, flight):
    with conn:
        sql = 'INSERT INTO flights VALUES(?, ?, ?, ?, ?, ?, ?)'
        cur = conn.cursor()
        cur.execute(sql, flight)
        return cur.lastrowid
