from os import getenv
import mysql.connector
from mysql.connector import pooling
import json
from datetime import datetime

from mt_connector.kpis import get_demo_kpis

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
    pool_size = 32,
    pool_reset_session = True,
    **db_config
  )

def get_connection():
  global cnx_pool
  if not cnx_pool:
    cnx_pool = init_connection_pool()
  return cnx_pool.get_connection()

def authenticate_user (token, account_type, account_number):
  cnx = get_connection()
  acc_type = 'demo' if account_type == 'DEMO' else 'live'
  key_field = f'{acc_type}Key'
  acc_num_field = f'{acc_type}AccountNumber'
  subscriptions_field = f'{acc_type}Subscriptions'
  sql = f"SELECT {key_field}, {acc_num_field}, {subscriptions_field} FROM Users WHERE {key_field} = %s AND {acc_num_field} = %s"
  c = cnx.cursor(dictionary=True)
  c.execute(sql, (token, account_number))
  user = c.fetchone()
  return json.loads(user[subscriptions_field]) if user else []

def get_strategy_demo_trades (magic):
  cnx = get_connection()
  sql = "SELECT demoStart, demoTrades FROM Strategies WHERE magic = %s"
  c = cnx.cursor(dictionary=True)
  c.execute(sql, (magic,))
  demo_trades = c.fetchone()
  return demo_trades

def update_strategy_demo_trades (magic, trades, kpis):
  cnx = get_connection()
  trades = json.dumps(trades)
  kpis = json.dumps(kpis)
  sql = "UPDATE Strategies SET demoTrades = %s, demoKpis = %s WHERE magic = %s"
  c = cnx.cursor()
  c.execute(sql, (trades, kpis, magic))
  cnx.commit()
  return bool(c.rowcount)

def add_trade_to_demo_trades (trade):
  demo_trade_data = get_strategy_demo_trades(trade['magic'])
  demo_start = demo_trade_data['demoStart']
  demo_trades = json.loads(demo_trade_data['demoTrades'])
  trades_with_order_id = [t for t in demo_trades if t['orderId'] == trade['orderId']]
  if not len(trades_with_order_id):
    demo_trades.append(trade)
    kpis = get_demo_kpis(demo_start, demo_trades)
    return update_strategy_demo_trades(trade['magic'], demo_trades, kpis)
  return False
