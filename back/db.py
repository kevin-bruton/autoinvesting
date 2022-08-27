from os import getenv
import mysql.connector
from mysql.connector import pooling
import json
from datetime import datetime

cnx_pool = None

def init_connection_pool():
  db_config = {
    'host': getenv('DB_SERVERNAME'),
    'user': getenv('DB_USERNAME'),
    'password': getenv('DB_PASSWORD'),
    'database': getenv('DB_NAME')
  }
  return mysql.connector.pooling.MySQLConnectionPool(
    pool_name = "db_pool",
    pool_size = 30,
    pool_reset_session = True,
    **db_config
  )

def get_connection():
  global cnx_pool
  if not cnx_pool:
    cnx_pool = init_connection_pool()
  return cnx_pool.get_connection()


def get_user (username, passwd):
  cnx = get_connection()
  sql = "SELECT * FROM Users WHERE username = %s AND passwd = %s"
  c = cnx.cursor()
  try:
    c.execute(sql, (username, passwd))
    user = c.fetchone()
  finally:
    cnx.close()
  return user

def get_strategies ():
  cnx = get_connection()
  # sql = "SELECT strategyName, magic, symbols, timeframes, btStart, btEnd, btDeposit, btKpis, demoStart, demoKpis FROM Strategies"
  sql = "SELECT * FROM Strategies"
  c = cnx.cursor(dictionary=True)
  try:
    c.execute(sql)
    strategies = c.fetchall()
  finally:
    cnx.close()
  return [{
    'strategyName': s['strategyName'],
    'magic': s['magic'],
    'symbols': s['symbols'],
    'timeframes': s['timeframes'],
    'btStart': str(s['btStart']),
    'btEnd': str(s['btEnd']),
    'btDeposit': s['btDeposit'],
    'btKpis': json.loads(s['btKpis']) if s['btKpis'] else {},
    'demoStart': str(s['demoStart']),
    'demoKpis': json.loads(s['demoKpis']) if s['demoKpis'] else {},
  } for s in strategies]

def get_all_strategy_data ():
  cnx = get_connection()
  sql = "SELECT strategyName,magic,symbols,timeframes,btStart,btEnd,btDeposit,btTrades,btKpis,demoStart,demoTrades,demoKpis FROM Strategies"
  c = cnx.cursor()
  try:
    c.execute(sql)
    strategies = c.fetchall() # returns a list of tuples
  finally:
    cnx.close()
  csv_str = 'strategyName;magic;symbols;timeframes;btStart;btEnd;btDeposit;btTrades;btKpis;demoStart;demoTrades;demoKpis\n'
  for s in strategies:
    csv_str += f"{s[0]};{s[1]};{s[2]};{s[3]};{s[4]};{s[5]};{s[6]};{s[7]};{s[8]};{s[9]};{s[10]};{s[11]}\n"
  return csv_str

def get_strategy_detail (magic):
  cnx = get_connection()
  sql = "SELECT * FROM Strategies WHERE magic = %s"
  c = cnx.cursor(dictionary=True)
  try:
    c.execute(sql, (magic,))
    s = c.fetchone()
  finally:
    cnx.disconnect()
  strategy = {
    'strategyName': s['strategyName'],
    'magic': s['magic'],
    'symbols': s['symbols'],
    'timeframes': s['timeframes'],
    'btStart': str(s['btStart']),
    'btEnd': str(s['btEnd']),
    'btDeposit': s['btDeposit'],
    'btTrades': json.loads(s['btTrades']) if s['btTrades'] else [],
    'btKpis': json.loads(s['btKpis']) if s['btKpis'] else {},
    'demoStart': str(s['demoStart']),
    'demoTrades': json.loads(s['demoTrades']) if s['demoTrades'] else [],
    'demoKpis': json.loads(s['demoKpis']) if s['demoKpis'] else {},
  }
  return strategy

def save_strategy (details):
  # print('SAVE STRATEGY DETAILS: ', details)
  cnx = get_connection()
  sql = "INSERT INTO Strategies (strategyName, magic, symbols, timeframes, btStart, btEnd, btTrades, btDeposit, btKpis, demoStart, demoTrades) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
  c = cnx.cursor()
  try:
    c.execute(sql, (details['strategyName'], details['magic'], details['symbols'], details['timeframes'], details['btStart'], details['btEnd'], details['btTrades'], details['btDeposit'], details['btKpis'], details['demoStart'], details['demoTrades']))
    cnx.commit()
    rowcount = c.rowcount
  finally:
    cnx.close()
  return bool(rowcount)

def save_backtest (data):
  if data['magic']:
    sql = "UPDATE Strategies SET btStart = %s, btEnd = %s, btDeposit = %s, btKpis = %s, btTrades = %s WHERE magic = %s"
    data_to_bind = (data['startDate'], data['endDate'], data['deposit'], json.dumps(data['kpis']), json.dumps(data['trades']), data['magic'])
  elif data['strategyName']:
    sql = "UPDATE Strategies SET btStart = %s, btEnd = %s, btDeposit = %s, btKpis = %s, btTrades = %s WHERE StrategyName = %s"
    data_to_bind = (data['startDate'], data['endDate'], data['deposit'], json.dumps(data['kpis']), json.dumps(data['trades']), data['strategyName'])
  else:
    raise Exception('A strategy name or magic must be provided')
  cnx = get_connection()
  c = cnx.cursor()
  try:
    c.execute(sql, data_to_bind)
    cnx.commit()
    rowcount = c.rowcount
  finally:
    cnx.close()
  return bool(rowcount)

def get_last_update ():
  sql = 'SELECT MAX(updateTime) FROM Updates'
  cnx = get_connection()
  c = cnx.cursor()
  try:
    c.execute(sql)
    last_update = c.fetchone()
  finally:
    cnx.disconnect()
  return last_update[0]

