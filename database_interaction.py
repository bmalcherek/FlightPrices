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
        sql = 'INSERT INTO flights VALUES(?, ?, ?, ?, ?, ?, ?, ?)'
        cur = conn.cursor()
        cur.execute(sql, flight)


def get_operator_id(conn, operator):
    with conn:
        sql = 'SELECT operator_id FROM operators WHERE operator_name = ?'
        cur = conn.cursor()
        cur.execute(sql, (operator, ))
        idx = cur.fetchall()

        if len(idx) == 0:
            return 'no such operator'

        return idx


def insert_operator(conn, operator):
    with conn:
        sql = 'INSERT INTO operators(operator_name) VALUES(?)'
        cur = conn.cursor()
        cur.execute(sql, (operator, ))


def get_flights_by_origin(conn, origin):
    with conn:
        sql = 'SELECT * FROM flights WHERE origin = ?'
        cur = conn.cursor()
        cur.execute(sql, (origin, ))

        return cur.fetchall()


def get_flights(conn, **kwargs):
    with conn:
        sql = 'SELECT * FROM flights '
        where = False
        for key, value in kwargs.items():
            if not(where):
                sql += f'WHERE {key} = "{value}" '
                where = True
            else:
                sql += f'AND {key} = "{value}"'

        cur = conn.cursor()
        cur.execute(sql)

        return cur.fetchall()
