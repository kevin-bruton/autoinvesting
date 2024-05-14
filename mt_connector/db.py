from os import getenv
import json
from datetime import datetime
"""
def get_demo_trades(cnx):
  sql = "SELECT magic, demoStart, demoTrades FROM Strategies"
  c = cnx.cursor(dictionary=True)
  c.execute(sql)
  demo_trades = c.fetchall()
  return demo_trades

def update_strategy_demo_trades(cnx, magic, trades, kpis):
  trades = json.dumps(trades)
  kpis = json.dumps(kpis)
  sql = "UPDATE Strategies SET demoTrades = ?, demoKpis = ? WHERE magic = ?"
  c = cnx.cursor()
  c.execute(sql, (trades, kpis, magic))
  cnx.commit()
  return bool(c.rowcount)

def update_demo_data(cnx, trades, kpis):
  magics = trades.keys()
  for magic in magics:
    update_strategy_demo_trades(cnx, magic, trades[magic], kpis[magic])

def register_update (result):
  now = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
  sql = 'INSERT INTO Updates (updateTime,result) VALUES (?, ?);'
  cnx = get_connection()
  c = cnx.cursor()
  try:
    c.execute(sql, (now, result))
    cnx.commit()
    rowcount = c.rowcount
  finally:
    cnx.close()
  return bool(rowcount)
"""
