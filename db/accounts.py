from os import getenv
from datetime import datetime
from collections import namedtuple
from db.common import mutate_many, mutate_one, query_many, query_one, values_placeholder

account_fields = 'accountId, accountType, broker, platform, username, balance, equity, lastConnectionUpdate, isConnected'
Account = namedtuple('Account', account_fields, defaults=(0, 0, None, None))

def get_accounts () -> list[Account]:
  sql = "SELECT accountId, accountType, broker, platform, username, balance, equity, strftime('%Y-%m-%d %H:%i:%S',lastConnectionUpdate) as lastConnectionUpdate, isConnected FROM Accounts"
  return query_many(sql)

def get_account_connection_status (account_id: str) -> bool:
  sql = 'SELECT isConnected FROM Accounts WHERE accountId = ?'
  is_connected = query_one(sql, (account_id,))
  return bool(is_connected)

def save_account (account: Account) -> int:
  sql = f"INSERT INTO Accounts ({account_fields}) VALUES ({values_placeholder(account_fields)})"
  return mutate_one(sql, account)

def update_account_username (accountId: str, username: str) -> int:
  sql = 'UPDATE Accounts SET username = ? WHERE accountId = ?'
  return mutate_one(sql, (username, accountId))

def set_connection_status (account_id: str, isConnected: bool) -> int:
  now = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
  sql = 'UPDATE Accounts SET lastConnectionUpdate = ?, isConnected = ? WHERE accountId = ?;'
  mutate_one(sql, (now, int(isConnected), account_id))

def get_platform_dir (account_id: str) -> str:
  sql = 'SELECT platformDir FROM Accounts WHERE accountId = ?'
  result = query_one(sql, (account_id,))
  if result and 'platformDir' in result.keys():
    return getenv('MT_INSTANCES_DIR') + result['platformDir'] + '/MQL4/Files/EaTemplates/'
  return None
