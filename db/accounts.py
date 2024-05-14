from datetime import datetime
from collections import namedtuple
from db.common import mutate_many, mutate_one, query_many, query_one, values_placeholder

account_fields = 'accountId, accountNumber, accountType, username, subscriptionKey, annualPctRet, maxDD, maxPctDD, annPctRetVsDdPct, winPct, profitFactor, numTrades, startDate, endDate, deposit'
Account = namedtuple('Account', account_fields, defaults=(None, None, None))

account_subscription_fields = 'accountId, subscriptions'
AccountSubscriptions = namedtuple('AccountSubscriptions', account_subscription_fields)

def get_accounts ():
  sql = "SELECT accountId, accountNumber, accountType, username, subscriptionKey, DATE_FORMAT(startDate, '%Y-%m-%d %H:%i:%S') as startDate, DATE_FORMAT(endDate, '%Y-%m-%d %H:%i:%S') as endDate, deposit, annualPctRet, maxDD, maxPctDD, annPctRetVsDdPct, winPct, profitFactor, numTrades FROM Accounts"
  return query_many(sql)

def get_account_id (account_number):
  sql = 'SELECT accountId FROM Accounts WHERE accountNumber = ?'
  row = query_many(sql, (account_number,))
  return row['accountId'] if row and 'accountId' in row else None

def get_account_connection_status (account_id):
  sql = 'SELECT isConnected FROM Accounts WHERE accountId = ?'
  is_connected = query_one(sql, (account_id,))
  return bool(is_connected)

def save_account (account):
  sql = f"INSERT INTO Accounts ({account_fields}) VALUES ({values_placeholder(account_fields)})"
  return mutate_one(sql, account)

def save_backtest (backtest):
  backtest = backtest._replace(accountType='strategy_backtest')
  sql = f"INSERT INTO Accounts ({account_fields}) VALUES ({values_placeholder(account_fields)})"
  return mutate_one(sql, backtest)

def save_demorun (demorun):
  demorun = demorun._replace(accountType='demo')
  sql = f"INSERT INTO Accounts ({account_fields}) VALUES ({values_placeholder(account_fields)})"
  return mutate_one(sql, demorun)

def save_account (account):
  sql = f"INSERT INTO Accounts ({account_fields}) VALUES ({values_placeholder(account_fields)})"
  return mutate_one(sql, account)

def update_account_username (accountId, username):
  sql = 'UPDATE Accounts SET username = ? WHERE accountId = ?'
  return mutate_one(sql, (username, accountId))

def update_kpis (accountId, start_date, deposit, kpis):
  sql = 'UPDATE Accounts SET startDate=?, deposit=?, annualPctRet=?, maxDD=?, maxPctDD=?, annPctRetVsDdPct=?, winPct=?, profitFactor=?, numTrades=? WHERE accountId=?'
  return mutate_one(sql, (start_date, deposit) + kpis + (accountId,))

def register_heartbeat (account_id):
  now = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
  sql = 'UPDATE Accounts SET lastHeartbeat = ? WHERE accountId = ?'
  mutate_one(sql, (now, account_id,))

def set_connection_status (account_id, isConnected):
  now = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
  sql = 'UPDATE Accounts SET lastConnectionUpdate = ?, isConnected = ? WHERE accountId = ?;'
  mutate_one(sql, (now, int(isConnected), account_id))

def authenticate_mt_client (token, account_number, account_type):
  sql = 'SELECT accountId FROM Accounts WHERE subscriptionKey = ? AND accountNumber = ? AND accountType = ?'
  user = query_one(sql, (token, account_number, account_type))
  if not user:
    return None
  sql = 'SELECT magic FROM Subscriptions, Accounts ' \
    + 'WHERE Accounts.subscriptionKey = ? ' \
    + 'AND Accounts.accountNumber = ? ' \
    + 'AND Accounts.accountType = ? ' \
    + 'AND Subscriptions.accountId = Accounts.accountId'
  subscriptions = mutate_many(sql, (token, account_number, account_type))
  magics = [s['magic'] for s in subscriptions]
  return AccountSubscriptions(user['accountId'], magics)
