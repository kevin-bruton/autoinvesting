from os import getenv
import mysql.connector
from mysql.connector import pooling
import json
from datetime import datetime
from operator import itemgetter
from collections import namedtuple

cnx_pool = None

values_placeholder = lambda fields: ','.join(['%s'] * len(fields.split(',')))

trade_fields = 'orderId, runId, symbol, orderType, openTime, closeTime, openPrice, closePrice, size, profit, closeType, comment, sl, tp, swap, commission'
Trade = namedtuple('Trade', trade_fields, defaults=(None, None, None, None, None, None))

strategyrun_fields = 'runId, magic, annualPctRet, maxDD, maxPctDD, annPctRetVsDdPct, winPct, profitFactor, numTrades, startDate, runType, endDate, deposit'
StrategyRun = namedtuple('StrategyRun', strategyrun_fields, defaults=(None, None, None))

strategy_fields = 'magic, strategyName, symbols, timeframes, description, workflow'
Strategy = namedtuple('Strategy', strategy_fields, defaults=(None, None))

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

def select_many (sql, params=()):
  cnx = get_connection()
  c = cnx.cursor(dictionary=True)
  try:
    c.execute(sql, tuple(params))
    rows = c.fetchall()
  finally:
    cnx.close()
  return rows

def select_one (sql, params=()):
  cnx = get_connection()
  c = cnx.cursor(dictionary=True)
  try:
    c.execute(sql, tuple(params))
    row = c.fetchone()
  finally:
    cnx.close()
  return row

def insert_one (sql, values):
  cnx = get_connection()
  c = cnx.cursor()
  try:
    c.execute(sql, tuple(values))
    cnx.commit()
    autoincrementedId = c.lastrowid
    rowcount = c.rowcount
  finally:
    cnx.close()
  if autoincrementedId:
    return autoincrementedId
  return bool(rowcount)

def update_one (sql, values):
  cnx = get_connection()
  c = cnx.cursor()
  try:
    c.execute(sql, tuple(values))
    cnx.commit()
  finally:
    cnx.close()
  return bool(c.rowcount)

def delete_many (sql, params=()):
  cnx = get_connection()
  c = cnx.cursor()
  try:
    c.execute(sql, tuple(params))
    cnx.commit()
  finally:
    cnx.close()
  return c.rowcount

def get_user (username, passwd):
  sql = "SELECT * FROM Users WHERE username = %s AND passwd = %s"
  return select_one(sql, (username, passwd))

def get_strategies ():
  # sql = "SELECT strategyName, magic, symbols, timeframes, btStart, btEnd, btDeposit, btKpis, demoStart, demoKpis FROM Strategies"
  sql = "SELECT strategyName, magic, symbols, timeframes, description, workflow FROM Strategies"
  return select_many(sql)

def get_strategy_runs ():
  sql = "SELECT runId, magic, runType, DATE_FORMAT(startDate, '%Y-%m-%d %H:%i:%S') as startDate, DATE_FORMAT(endDate, '%Y-%m-%d %H:%i:%S') as endDate, deposit, annualPctRet, maxDD, maxPctDD, annPctRetVsDdPct, winPct, profitFactor, numTrades FROM StrategyRuns"
  return select_many(sql)

def get_trades ():
  sql = 'SELECT orderId, runId, symbol, orderType, openTime, closeTime, openPrice, closePrice, size, profit, closeType, comment FROM Trades'
  trades = select_many(sql)
  return [{**trade, **{
      'openTime': trade['openTime'].strftime('%Y-%m-%d %H:%M:%S'),
      'closeTime': trade['closeTime'].strftime('%Y-%m-%d %H:%M:%S'),
      'size': float(trade['size']),
      'profit': float(trade['profit'])
    }} for trade in trades]

def get_trades_of_strategyrun (run_id):
  sql = 'SELECT symbol, orderType, openTime, closeTime, openPrice, closePrice, size, profit, closeType, comment FROM Trades WHERE runId = %s ORDER BY closeTime'
  trades = select_many(sql, (run_id,))
  return [{**trade, **{
      'openTime': trade['openTime'].strftime('%Y-%m-%d %H:%M:%S'),
      'closeTime': trade['closeTime'].strftime('%Y-%m-%d %H:%M:%S'),
      'size': float(trade['size']),
      'profit': float(trade['profit'])
    }} for trade in trades]

def get_next_free_order_id ():
  trades = get_trades()
  order_ids = [trade['orderId'] for trade in trades]
  for test_order_id in range(len(order_ids) + 1):
    if test_order_id not in order_ids:
      return test_order_id

def get_all_kpis ():
  sql = 'SELECT magic, runType, annualPctRet, maxDD, maxPctDD, annPctRetVsDdPct, winPct, profitFactor, numTrades ' \
    + 'FROM StrategyRuns'
  return select_many(sql)

def get_strategys_demo_trades (magic):
  runId = str(magic) + '_D'
  sql = 'SELECT orderId, runId, symbol, orderType, openTime, closeTime, openPrice, closePrice, size, profit, closeType, comment ' \
    + 'FROM Trades WHERE runId = %s'
  return select_many(sql, (runId,))

def get_strategy_summaries ():
  strategies = get_strategies()
  kpis_list = get_all_kpis()
  #return { 'strategies': strategies, 'kpis_list': kpis_list }
  for strategy in strategies:
    for strategy_kpis in kpis_list:
      if strategy_kpis['magic'] == strategy['magic']:
        run = {
          'annualPctRet': float(strategy_kpis['annualPctRet']),
          'maxDD': float(strategy_kpis['maxDD']),
          'maxPctDD': float(strategy_kpis['maxPctDD']),
          'annPctRetVsDdPct': float(strategy_kpis['annPctRetVsDdPct']),
          'winPct': float(strategy_kpis['winPct']),
          'profitFactor': float(strategy_kpis['profitFactor']),
          'numTrades': float(strategy_kpis['numTrades'])
        }
        strategy[strategy_kpis['runType']] = run
  return strategies

def get_strategy_detail (magic):
  sql = "SELECT strategyName, symbols, timeframes, workflow, description FROM Strategies WHERE magic = %s"
  strategy = select_one(sql, (magic,))
  sql = 'SELECT runId, startDate, endDate, deposit, annualPctRet, maxDD, maxPctDD, annPctRetVsDdPct, winPct, profitFactor, numTrades FROM StrategyRuns WHERE magic = %s AND runType = %s'
  backtest = select_one(sql, (magic, 'backtest'))
  sql = 'SELECT runId, startDate, annualPctRet, maxDD, maxPctDD, annPctRetVsDdPct, winPct, profitFactor, numTrades FROM StrategyRuns WHERE magic = %s AND runType = %s'
  demo = select_one(sql, (magic, 'demo'))
  btTrades = get_trades_of_strategyrun(backtest['runId'])
  demoTrades = get_trades_of_strategyrun(demo['runId'])
  btKpis = {
    'annualPctRet': backtest['annualPctRet'],
    'maxDD': backtest['maxDD'],
    'maxPctDD': backtest['maxPctDD'],
    'annPctRetVsDdPct': backtest['annPctRetVsDdPct'],
    'winPct': backtest['winPct'],
    'profitFactor': backtest['profitFactor'],
    'numTrades': backtest['numTrades']
  }
  demoKpis = {
    'annualPctRet': demo['annualPctRet'],
    'maxDD': demo['maxDD'],
    'maxPctDD': demo['maxPctDD'],
    'annPctRetVsDdPct': demo['annPctRetVsDdPct'],
    'winPct': demo['winPct'],
    'profitFactor': demo['profitFactor'],
    'numTrades': demo['numTrades']
  }
  strategy = {
    'strategyName': strategy['strategyName'],
    'magic': magic,
    'symbols': strategy['symbols'],
    'timeframes': strategy['timeframes'],
    'btStart': str(backtest['startDate']),
    'btEnd': str(backtest['endDate']),
    'btDeposit': backtest['deposit'],
    'btTrades': btTrades if btTrades else [],
    'btKpis': btKpis,
    'demoStart': str(demo['startDate']),
    'demoTrades': demoTrades if demoTrades else [],
    'demoKpis': demoKpis
  }
  return strategy

def save_strategy (strategy):
  sql = f"INSERT INTO Strategies ({strategy_fields}) VALUES ({values_placeholder(strategy_fields)})"
  return insert_one(sql, strategy)

def save_backtest (backtest):
  backtest = backtest._replace(runType='backtest')
  sql = f"INSERT INTO StrategyRuns ({strategyrun_fields}) VALUES ({values_placeholder(strategyrun_fields)})"
  return insert_one(sql, backtest)

def save_demorun (demorun):
  demorun = demorun._replace(runType='demo')
  sql = f"INSERT INTO StrategyRuns ({strategyrun_fields}) VALUES ({values_placeholder(strategyrun_fields)})"
  return insert_one(sql, demorun)

def save_strategyrun (strategyrun):
  sql = f"INSERT INTO StrategyRuns ({strategyrun_fields}) VALUES ({values_placeholder(strategyrun_fields)})"
  return insert_one(sql, strategyrun)

def save_trade (trade_values):
  sql = f"INSERT INTO Trades ({trade_fields}) VALUES ({values_placeholder(trade_fields)})"
  return insert_one(sql, trade_values)
  
def get_all_strategy_data ():
  """ Get all strategy data from old db structure """
  sql = "SELECT strategyName,magic,symbols,timeframes,btStart,btEnd,btDeposit,btTrades,btKpis,demoStart,demoTrades,demoKpis FROM Strategies"
  return select_many(sql)

def update_kpis (runId, start_date, deposit, kpis):
  sql = 'UPDATE StrategyRuns SET startDate=%s, deposit=%s, annualPctRet=%s, maxDD=%s, maxPctDD=%s, annPctRetVsDdPct=%s, winPct=%s, profitFactor=%s, numTrades=%s WHERE runId=%s'
  return update_one(sql, (start_date, deposit) + kpis + (runId,))

def get_strategies_and_kpis ():
  pass

""" def get_all_strategy_data_as_csv ():
  strategies = get_all_strategy_data()
  csv_str = 'strategyName;magic;symbols;timeframes;btStart;btEnd;btDeposit;btTrades;btKpis;demoStart;demoTrades;demoKpis\n'
  for s in strategies:
    csv_str += f"{s[0]};{s[1]};{s[2]};{s[3]};{s[4]};{s[5]};{s[6]};{s[7]};{s[8]};{s[9]};{s[10]};{s[11]}\n"
  return csv_str """

""" def save_strategy (details):
  # print('SAVE STRATEGY DETAILS: ', details)
  strategy_values = (details['strategyName'], details['magic'], details['symbols'], details['timeframes'])
  sql = 'INSERT INTO Strategies (strategyName, magic, symbols, timeframes) VALUES (%s,%s,%s,%s)'
  strategy_inserted = insert_one(sql, strategy_values)
  btKpis = details['btKpis']
  demoKpis = details['demoKpis']
  backtest = [
    details['btStart'],
    details['btEnd'],
    details['btDeposit'],
    btKpis['annualPctRet'],
    btKpis['maxDD'],
    btKpis['maxPctDD'],
    btKpis['annPctRetVsDdPct'],
    btKpis['winPct'],
    btKpis['profitFactor'],
    btKpis['numTrades']
  ]
  demorun = [
    details['demoStart'],
    demoKpis['annualPctRet'],
    demoKpis['maxDD'],
    demoKpis['maxPctDD'],
    demoKpis['annPctRetVsDdPct'],
    demoKpis['winPct'],
    demoKpis['profitFactor'],
    demoKpis['numTrades']
  ]
  if strategy_inserted:
    bt_run_id = save_backtest(details['magic'], backtest)
    demo_run_id = save_demorun(details['magic'], demorun)
    if bt_run_id:
      for trade in details['btTrades']:
        save_trade(bt_run_id, trade.values())
    if demo_run_id:
      for trade in details['demoTrades']:
        save_trade(demo_run_id, trade.values()) """
      

""" def save_kpis (runId, annualPctRet, maxDD, maxPctDD, annPctRetVsDdPct, winPct, profitFactor, numTrades):
  cnx = get_connection()
  sql = "INSERT INTO Kpis (runId, annualPctRet, maxDD, maxPctDD, annPctRetVsDdPct, winPct, profitFactor, numTrades) VALUES (%s,%s,%s,%s,%s,%s,%s,%s);"
  c = cnx.cursor()
  try:
    c.execute(sql, (runId, annualPctRet, maxDD, maxPctDD, annPctRetVsDdPct, winPct, profitFactor, numTrades))
    cnx.commit()
    rowcount = c.rowcount
  finally:
    cnx.close()
  return bool(rowcount) """

""" DEPRECATED """
""" def save_backtest_legacy (bt):
  if bt['magic']:
    sql = "UPDATE Strategies SET btStart = %s, btEnd = %s, btDeposit = %s, btKpis = %s, btTrades = %s WHERE magic = %s"
    data_to_bind = (bt['startDate'], bt['endDate'], bt['deposit'], json.dumps(bt['kpis']), json.dumps(bt['trades']), bt['magic'])
  elif bt['strategyName']:
    sql = "UPDATE Strategies SET btStart = %s, btEnd = %s, btDeposit = %s, btKpis = %s, btTrades = %s WHERE StrategyName = %s"
    data_to_bind = (bt['startDate'], bt['endDate'], bt['deposit'], json.dumps(bt['kpis']), json.dumps(bt['trades']), bt['strategyName'])
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
  return bool(rowcount) """

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

def register_update (result):
  now = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
  sql = 'INSERT INTO Updates (updateTime,result) VALUES (%s, %s);'
  return insert_one(sql, (now, result))

if __name__ == '__main__':
  from dotenv import load_dotenv
  load_dotenv()
  strategies = get_strategy_summaries()
  print(strategies[0])
  """ for strategy in strategies:
    print(strategy) """
