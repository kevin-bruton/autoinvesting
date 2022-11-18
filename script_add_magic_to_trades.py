from dotenv import load_dotenv

from mt_connector.connector import mt_connector_client
import back.db as db
from back.db import Trade

load_dotenv()

""" trades = db.get_trades()

for trade in trades:
  if trade['magic'] == None:
    magic = trade['accountId'][:-2]
    result = db.update_trade_magic(trade['orderId'], magic)
    print("\U00002705", end='') if result else print("\U0000274C", end='') """


accounts = db.get_accounts()

for account in accounts:
  if account['username'] == None:
    result = db.update_account_username(account['accountId'], 'master')
    print("\U00002705", end='') if result else print("\U0000274C", end='')