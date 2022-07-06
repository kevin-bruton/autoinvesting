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
  c.execute(sql, (username, passwd))
  user = c.fetchone()
  cnx.close()
  return user

def get_strategies ():
  cnx = get_connection()
  sql = "SELECT * FROM Strategies"
  c = cnx.cursor(dictionary=True)
  c.execute(sql)
  strategies = c.fetchall()
  cnx.close()
  return strategies

def save_strategy (details):
  print('SAVE STRATEGY DETAILS: ', details)
  cnx = get_connection()
  sql = "INSERT INTO Strategies (strategyName, magic, symbols, timeframes, demoStart, mq4StrategyFile, sqxStrategyFile) VALUES (%s,%s,%s,%s,%s,%s,%s)"
  c = cnx.cursor()
  c.execute(sql, (details['strategyName'], details['magic'], details['symbols'], details['timeframes'], details['demoStart'], details['mq4StrategyFile'], details['sqxStrategyFile']))
  cnx.commit()
  rowcount = c.rowcount
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
  c.execute(sql, data_to_bind)
  cnx.commit()
  rowcount = c.rowcount
  cnx.close()
  return bool(rowcount)
  
