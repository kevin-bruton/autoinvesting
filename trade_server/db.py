from os import getenv
import json
from back import db

from back.utils import get_demo_kpis

def authenticate_user (token, account_type, account_number):
  cnx = db.get_connection()
  acc_type = 'demo' if account_type == 'DEMO' else 'live'
  key_field = f'{acc_type}Key'
  acc_num_field = f'{acc_type}AccountNumber'
  subscriptions_field = f'{acc_type}Subscriptions'
  sql = f"SELECT {key_field}, {acc_num_field}, {subscriptions_field} FROM Users WHERE {key_field} = %s AND {acc_num_field} = %s"
  c = cnx.cursor(dictionary=True)
  try: 
    c.execute(sql, (token, account_number))
    user = c.fetchone()
  finally:
    cnx.close()
  return json.loads(user[subscriptions_field]) if user else []

def get_strategy_demo_trades (magic):
  sql = 'SELECT runId, startDate FROM StrategyRuns WHERE magic = %s AND runType = %s'
  demo = db.select_one(sql, (magic, 'demo'))
  print('demo:', demo)
  sql = 'SELECT * FROM Trades WHERE runId = %s'
  trades = db.select_many(sql, (demo['runId'],))
  return { 'demoStart': demo['startDate'], 'demoTrades': trades }

def update_strategy_demo_trades (magic, trades, kpis):
  """ sql = 'UPDATE Strategies SET demoTrades = %s, demoKpis = %s WHERE magic = %s'
  return db.update_one(sql, (trades, kpis, magic)) """



def add_trade_to_demo_trades (trade):
  demo_trade_data = get_strategy_demo_trades(trade['magic'])
  print('trade_data:', demo_trade_data)
  demo_start = demo_trade_data['demoStart']
  demo_trades = demo_trade_data['demoTrades']
  trades_with_order_id = [t for t in demo_trades if t['orderId'] == trade['orderId']]
  if not len(trades_with_order_id):
    demo_trades.append(trade)
    kpis = get_demo_kpis(demo_start, demo_trades)
    return update_strategy_demo_trades(trade['magic'], demo_trades, kpis)
  return False
