from os import getenv
import mysql.connector
import json

def get_connection():
  return mysql.connector.connect(
    host= getenv('DB_SERVERNAME'),
    user= getenv('DB_USERNAME'),
    password= getenv('DB_PASSWORD'),
    database= getenv('DB_NAME')
  )

def get_demo_trades(cnx):
  sql = "SELECT magic, demoStart, demoTrades FROM Strategies"
  c = cnx.cursor(dictionary=True)
  c.execute(sql)
  demo_trades = c.fetchall()
  return demo_trades

def update_strategy_demo_trades(cnx, magic, trades, kpis):
  trades = json.dumps(trades)
  kpis = json.dumps(kpis)
  sql = "UPDATE Strategies SET demoTrades = %s, demoKpis = %s WHERE magic = %s"
  c = cnx.cursor()
  c.execute(sql, (trades, kpis, magic))
  cnx.commit()
  return bool(c.rowcount)

def update_demo_data(cnx, trades, kpis):
  magics = trades.keys()
  for magic in magics:
    update_strategy_demo_trades(cnx, magic, trades[magic], kpis[magic])


