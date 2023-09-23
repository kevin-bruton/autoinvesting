from os import getenv
import mysql.connector
from mysql.connector import pooling
import json
from datetime import datetime
from operator import itemgetter
from collections import namedtuple

cnx_pool = None
datetime_fmt = '%Y-%m-%d %H:%M:%S'
values_placeholder = lambda fields: ','.join(['%s'] * len(fields.split(',')))

user_fields = 'accountType, username, passwd, email, firstName, lastName, city, country'
User = namedtuple('User', user_fields, defaults=(None, None))

trade_fields = 'orderId, masterOrderId, accountId, magic, symbol, orderType, openTime, closeTime, openPrice, closePrice, size, profit, balance, closeType, comment, sl, tp, swap, commission'
Trade = namedtuple('Trade', trade_fields, defaults=(None, None, None, None, None, None))

order_fields = 'orderId, masterOrderId, accountId, magic, symbol, orderType, openTime, openPrice, size, comment, sl, tp, status'
Order = namedtuple('Order', order_fields)

account_fields = 'accountId, accountNumber, accountType, username, subscriptionKey, annualPctRet, maxDD, maxPctDD, annPctRetVsDdPct, winPct, profitFactor, numTrades, startDate, endDate, deposit'
Account = namedtuple('Account', account_fields, defaults=(None, None, None))

strategy_fields = 'magic, strategyName, symbols, timeframes, description, workflow'
Strategy = namedtuple('Strategy', strategy_fields, defaults=(None, None))

subscription_fields = 'magicAccountId,accountId, magic'
Subscription = namedtuple('Subscription', subscription_fields)

account_subscription_fields = 'accountId, subscriptions'
AccountSubscriptions = namedtuple('AccountSubscriptions', account_subscription_fields)

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
  autoincrementedId = None
  rowcount = False
  try:
    c.execute(sql, tuple(values))
    cnx.commit()
    autoincrementedId = c.lastrowid
    rowcount = c.rowcount
  except Exception as e:
    if 'Duplicate entry' not in repr(e):
      print('ERROR CAUGHT INSERT ONE. VALUES:', values, '; MESSAGE:', repr(e))
    raise Exception(e)
  finally:
    cnx.close()
  if autoincrementedId:
    return autoincrementedId
  return bool(rowcount)

def insert_many (sql, values): # values is a tuple of tuples
  cnx = get_connection()
  c = cnx.cursor()
  autoincrementedId = None
  rowcount = False
  try:
    c.executemany(sql, values)
    cnx.commit()
    autoincrementedId = c.lastrowid
    rowcount = c.rowcount
  except Exception as e:
    if 'Duplicate entry' not in repr(e):
      print('ERROR CAUGHT INSERT ONE. VALUES:', values, '; MESSAGE:', repr(e))
    raise Exception(e)
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

def get_users ():
  sql = 'SELECT username, passwd, email, firstName, lastName, city, country, accountType FROM Users'
  return select_many(sql)

def get_user (username, passwd):
  sql = "SELECT * FROM Users WHERE username = %s AND passwd = %s"
  return select_one(sql, (username, passwd))

def get_strategies ():
  # sql = "SELECT strategyName, magic, symbols, timeframes, btStart, btEnd, btDeposit, btKpis, demoStart, demoKpis FROM Strategies"
  sql = "SELECT strategyName, magic, symbols, timeframes, description, workflow FROM Strategies"
  return select_many(sql)

def get_accounts ():
  sql = "SELECT accountId, accountNumber, accountType, username, subscriptionKey, DATE_FORMAT(startDate, '%Y-%m-%d %H:%i:%S') as startDate, DATE_FORMAT(endDate, '%Y-%m-%d %H:%i:%S') as endDate, deposit, annualPctRet, maxDD, maxPctDD, annPctRetVsDdPct, winPct, profitFactor, numTrades FROM Accounts"
  return select_many(sql)

def get_account_id (account_number):
  sql = 'SELECT accountId FROM Accounts WHERE accountNumber = %s'
  row = select_one(sql, (account_number,))
  return row['accountId'] if row and 'accountId' in row else None

def get_subscriptions ():
  sql = 'SELECT magicAccountId, accountId, magic FROM Subscriptions'
  return select_many(sql)

def get_orders ():
  sql = f'SELECT {order_fields} FROM Orders'
  orders = select_many(sql)
  return [{**order, **{
    'openTime': order['openTime'].strftime('%Y-%m-%d %H:%M:%S')
  }} for order in orders]

def get_trades ():
  sql = f'SELECT {trade_fields} FROM Trades'
  trades = select_many(sql)
  return [{**trade, **{
      'openTime': trade['openTime'].strftime('%Y-%m-%d %H:%M:%S'),
      'closeTime': trade['closeTime'].strftime('%Y-%m-%d %H:%M:%S'),
      'size': float(trade['size']),
      'profit': float(trade['profit'])
    }} for trade in trades]

def get_trades_of_account (account_id):
  sql = 'SELECT symbol, orderType, openTime, closeTime, openPrice, closePrice, size, profit, closeType, comment FROM Trades WHERE accountId = %s ORDER BY closeTime'
  trades = select_many(sql, (account_id,))
  return [{**trade, **{
      'openTime': trade['openTime'].strftime(datetime_fmt),
      'closeTime': trade['closeTime'].strftime(datetime_fmt),
      'size': float(trade['size']),
      'profit': float(trade['profit'])
    }} for trade in trades]

def get_next_free_order_id ():
  trades = get_trades()
  order_ids = [trade['orderId'] for trade in trades]
  for test_order_id in range(len(order_ids) + 1):
    if test_order_id not in order_ids:
      return test_order_id

def get_corresponding_orderid (masterOrderId, accountId):
  sql = 'SELECT orderId FROM Orders WHERE masterOrderId = %s AND accountId = %s'
  row = select_one(sql, (masterOrderId, accountId))
  return row['orderId'] if row != None else None

def get_order (order_id):
  sql = f"SELECT {order_fields} FROM Orders WHERE orderId = %s"
  row = select_one(sql, (order_id,))
  return row

def get_users_account_ids (username):
  sql = 'SELECT accountId FROM Accounts WHERE username = %s'
  return [a['accountId'] for a in select_many(sql, (username,))]

def get_account_orders (account_id):
  sql = 'SELECT * FROM Orders WHERE accountId = %s'
  orders = select_many(sql, (account_id,))
  return [{**o, **{
    'openTime': o['openTime'].strftime(datetime_fmt),
    'size': float(o['size'])
  }} for o in orders]

def get_account_trades (account_id):
  sql = 'SELECT * FROM Trades WHERE accountId = %s'
  trades = select_many(sql, (account_id,))
  return [{**t, **{
    'openTime': t['openTime'].strftime(datetime_fmt),
    'closeTime': t['closeTime'].strftime(datetime_fmt),
    'openPrice': float(t['openPrice']),
    'closePrice': float(t['closePrice']),
    'size': float(t['size']),
    'profit': float(t['profit']),
    'balance': float(t['balance']) if t['balance'] else 0,
    'sl': float(t['sl']) if t['sl'] else None,
    'tp': float(t['tp']) if t['tp'] else None,
    'swap': float(t['swap']) if t['swap'] else 0,
    'commission': float(t['commission']) if t['commission'] else 0
    }} for t in trades]

def get_account_connection_status (account_id):
  sql = 'SELECT isConnected FROM Accounts WHERE accountId = %s'
  is_connected = select_one(sql, (account_id,))
  return bool(is_connected)

def update_subscriptions (account_id, magics):
  sql = 'DELETE FROM Subscriptions WHERE accountId = %s'
  delete_many(sql, (account_id,))
  sql = 'INSERT INTO Subscriptions (magicAccountId, magic, accountId) VALUES (%s,%s,%s)'
  values = [(f"{magic}_{account_id}", magic, account_id) for magic in magics]
  insert_many(sql, values)

def get_all_strategy_kpis ():
  sql = 'SELECT accountNumber, accountType, annualPctRet, maxDD, maxPctDD, annPctRetVsDdPct, winPct, profitFactor, numTrades ' \
    + 'FROM Accounts WHERE accountType = %s OR accountType = %s'
  kpis = select_many(sql, ('strategy_backtest', 'strategy_demo'))
  return [ {
    'runType': 'backtest' if kpi['accountType'] == 'strategy_backtest' else 'demo',
    'magic': int(kpi['accountNumber']),
    'annualPctRet': float(kpi['annualPctRet']) if kpi['annualPctRet'] != None else None,
    'maxDD': float(kpi['maxDD']) if kpi['maxDD'] != None else None,
    'maxPctDD': float(kpi['maxPctDD']) if kpi['maxPctDD'] != None else None,
    'annPctRetVsDdPct': float(kpi['annPctRetVsDdPct']) if kpi['annPctRetVsDdPct'] != None else None,
    'winPct': float(kpi['winPct']) if kpi['winPct'] != None else None,
    'profitFactor': float(kpi['profitFactor']) if kpi['profitFactor'] != None else None,
    'numTrades': float(kpi['numTrades']) if kpi['numTrades'] != None else None
  } for kpi in kpis if kpi['accountType'] == 'strategy_backtest' or kpi['accountType'] == 'strategy_demo']

def get_strategys_demo_trades (magic):
  accountId = str(magic) + '_D'
  sql = 'SELECT orderId, accountId, symbol, orderType, openTime, closeTime, openPrice, closePrice, size, profit, closeType, comment ' \
    + 'FROM Trades WHERE accountId = %s'
  return select_many(sql, (accountId,))

def get_strategys_backtest_trades (magic):
  accountId = str(magic) + '_B'
  sql = 'SELECT orderId, accountId, symbol, orderType, openTime, closeTime, openPrice, closePrice, size, profit, closeType, comment ' \
    + 'FROM Trades WHERE accountId = %s'
  return select_many(sql, (accountId,))

def get_strategys_combined_trades (magic):
  backtest_trades = get_strategys_backtest_trades(magic)
  demo_trades = get_strategys_demo_trades(magic)
  return backtest_trades.extend(demo_trades)

def get_strategy_summaries ():
  strategies = get_strategies()
  kpis_list = get_all_strategy_kpis()
  #return { 'strategies': strategies, 'kpis_list': kpis_list }
  for strategy in strategies:
    for strategy_kpis in kpis_list:
      if strategy_kpis['magic'] == strategy['magic']:
        runType = strategy_kpis['runType']
        run = { kpi:kpi_val for kpi, kpi_val in strategy_kpis.items() if kpi != 'runType' }
        strategy[runType] = run
  return strategies

def get_strategy_detail (magic):
  sql = "SELECT strategyName, symbols, timeframes, workflow, description FROM Strategies WHERE magic = %s"
  strategy = select_one(sql, (magic,))
  sql = 'SELECT accountId, startDate, endDate, deposit, annualPctRet, maxDD, maxPctDD, annPctRetVsDdPct, winPct, profitFactor, numTrades FROM Accounts WHERE accountNumber = %s AND accountType = %s'
  backtest = select_one(sql, (magic, 'strategy_backtest'))
  sql = 'SELECT accountId, startDate, annualPctRet, maxDD, maxPctDD, annPctRetVsDdPct, winPct, profitFactor, numTrades FROM Accounts WHERE accountNumber = %s AND accountType = %s'
  demo = select_one(sql, (magic, 'strategy_demo'))
  btTrades = get_trades_of_account(backtest['accountId'])
  demoTrades = get_trades_of_account(demo['accountId'])
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

def save_user (user):
  sql = f"INSERT INTO Users ({user_fields}) VALUES ({values_placeholder(user_fields)})"
  return insert_one(sql, user)

def save_strategy (strategy):
  sql = f"INSERT INTO Strategies ({strategy_fields}) VALUES ({values_placeholder(strategy_fields)})"
  return insert_one(sql, strategy)

def save_account (account):
  sql = f"INSERT INTO Accounts ({account_fields}) VALUES ({values_placeholder(account_fields)})"
  return insert_one(sql, account)

def save_order (order):
  sql = f"INSERT INTO Orders ({order_fields}) VALUES ({values_placeholder(order_fields)})"
  return insert_one(sql, order)

def save_subscription (subscription):
  sql = f"INSERT INTO Subscriptions ({subscription_fields}) VALUES ({values_placeholder(subscription_fields)})"
  return insert_one(sql, subscription)

def save_backtest (backtest):
  backtest = backtest._replace(accountType='strategy_backtest')
  sql = f"INSERT INTO Accounts ({account_fields}) VALUES ({values_placeholder(account_fields)})"
  return insert_one(sql, backtest)

def save_demorun (demorun):
  demorun = demorun._replace(accountType='demo')
  sql = f"INSERT INTO Accounts ({account_fields}) VALUES ({values_placeholder(account_fields)})"
  return insert_one(sql, demorun)

def save_account (account):
  sql = f"INSERT INTO Accounts ({account_fields}) VALUES ({values_placeholder(account_fields)})"
  return insert_one(sql, account)

def save_trade (trade_values):
  sql = f"INSERT INTO Trades ({trade_fields}) VALUES ({values_placeholder(trade_fields)})"
  return insert_one(sql, trade_values)
  
def get_all_strategy_data ():
  """ Get all strategy data from old db structure """
  sql = "SELECT strategyName,magic,symbols,timeframes,btStart,btEnd,btDeposit,btTrades,btKpis,demoStart,demoTrades,demoKpis FROM Strategies"
  return select_many(sql)

def update_trade_magic (orderId, magic):
  sql = 'UPDATE Trades SET magic = %s WHERE orderId = %s'
  return update_one(sql, (magic, orderId,))

def update_account_username (accountId, username):
  sql = 'UPDATE Accounts SET username = %s WHERE accountId = %s'
  return update_one(sql, (username, accountId))

def update_kpis (accountId, start_date, deposit, kpis):
  sql = 'UPDATE Accounts SET startDate=%s, deposit=%s, annualPctRet=%s, maxDD=%s, maxPctDD=%s, annPctRetVsDdPct=%s, winPct=%s, profitFactor=%s, numTrades=%s WHERE accountId=%s'
  return update_one(sql, (start_date, deposit) + kpis + (accountId,))

def update_order_status (orderId, status):
  sql = 'UPDATE Orders SET status = %s WHERE orderId = %s'
  return update_one(sql, (status, orderId))

def delete_order (order_id):
  sql = 'DELETE From Orders WHERE orderId = %s'
  return delete_many(sql, (order_id,))

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

def register_heartbeat (account_id):
  now = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
  sql = 'UPDATE Accounts SET lastHeartbeat = %s WHERE accountId = %s'
  update_one(sql, (now, account_id,))

def set_connection_status (account_id, isConnected):
  now = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
  sql = 'UPDATE Accounts SET lastConnectionUpdate = %s, isConnected = %s WHERE accountId = %s;'
  update_one(sql, (now, int(isConnected), account_id))

def authenticate_mt_client (token, account_number, account_type):
  sql = 'SELECT accountId FROM Accounts WHERE subscriptionKey = %s AND accountNumber = %s AND accountType = %s'
  user = select_one(sql, (token, account_number, account_type))
  if not user:
    return None
  sql = 'SELECT magic FROM Subscriptions, Accounts ' \
    + 'WHERE Accounts.subscriptionKey = %s ' \
    + 'AND Accounts.accountNumber = %s ' \
    + 'AND Accounts.accountType = %s ' \
    + 'AND Subscriptions.accountId = Accounts.accountId'
  subscriptions = select_many(sql, (token, account_number, account_type))
  magics = [s['magic'] for s in subscriptions]
  return AccountSubscriptions(user['accountId'], magics)

def get_accounts_subscriptions (account_id):
  sql = 'SELECT magic FROM Subscriptions WHERE accountId = %s'
  subscriptions = select_many(sql, (account_id,))
  magics = [s['magic'] for s in subscriptions]
  return magics

def get_accounts_subscribed_to_magic (magic):
  sql = 'SELECT accountId FROM Subscriptions WHERE magic = %s'
  results = select_many(sql, (magic,))
  return [r['accountId'] for r in results]

if __name__ == '__main__':
  from dotenv import load_dotenv
  load_dotenv()
  subscriptions = authenticate_mt_client('GwD22oS3@KRp', '612940', 'demo')
  print(subscriptions)
  """ for strategy in strategies:
    print(strategy) """
