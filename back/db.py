from os import getenv
import mysql.connector
from mysql.connector import pooling
import json

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
    pool_size = 3,
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
  sql = "SELECT * FROM Strategies"
  c = cnx.cursor(dictionary=True)
  try:
    c.execute(sql)
    strategies = c.fetchall()
  finally:
    cnx.close()
  return strategies

def get_strategy_detail (magic):
  cnx = get_connection()
  sql = "SELECT * FROM Strategies WHERE magic = %s"
  c = cnx.cursor(dictionary=True)
  try:
    c.execute(sql, (magic,))
    strategy = c.fetchone()
  finally:
    cnx.disconnect()
  return strategy

def save_strategy (details):
  # print('SAVE STRATEGY DETAILS: ', details)
  cnx = get_connection()
  sql = "INSERT INTO Strategies (strategyName, magic, symbols, timeframes, btStart, btEnd, btTrades, btDeposit, demoStart, demoTrades) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
  c = cnx.cursor()
  try:
    c.execute(sql, (details['strategyName'], details['magic'], details['symbols'], details['timeframes'], details['btStart'], details['btEnd'], details['btTrades'], details['btDeposit'], details['demoStart'], details['demoTrades']))
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
  
