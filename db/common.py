import sqlite3
from os import getenv

db_path = getenv('DB_FILE')
datetime_fmt = '%Y-%m-%d %H:%M:%S'
values_placeholder = lambda fields: ','.join(['?'] * len(fields.split(',')))

def mutate_one(sql, values: tuple):
  ''' UPDATE, INSERT, DELETE'''
  conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
  rows_affected = 0
  try:
    c = conn.cursor()
    c.execute(sql, values)
    conn.commit()
    rows_affected = c.rowcount
  finally:
    conn.close()
  return rows_affected

def mutate_many(sql, values: list[tuple]):
  ''' UPDATE, INSERT, DELETE'''
  conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
  rows_affected = 0
  try:
    c = conn.cursor()
    c.executemany(sql, values)
    conn.commit()
    rows_affected = c.rowcount
  finally:
    conn.close()
  return rows_affected

def query_one(sql, values=()):
  conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
  try:
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute(sql, values)
    result = c.fetchone()
    return result
  finally:
    conn.close()


def query_many(sql, values: list[tuple] = None):
  conn = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
  try:
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.row_factory = sqlite3.Row
    c.execute(sql, values) if values else c.execute(sql)
    result = c.fetchall()
    return result
  finally:
    conn.close()
