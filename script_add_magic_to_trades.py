from dotenv import load_dotenv

from db2.accounts import get_accounts, update_account_username
from mt_connector.connector import mt_connector_client

load_dotenv()

""" trades = db.get_trades()

for trade in trades:
  if trade['magic'] == None:
    magic = trade['accountId'][:-2]
    result = db.update_trade_magic(trade['orderId'], magic)
    print("\U00002705", end='') if result else print("\U0000274C", end='') """


accounts = get_accounts()

for account in accounts:
  if account['username'] == None:
    result = update_account_username(account['accountId'], 'master')
    print("\U00002705", end='') if result else print("\U0000274C", end='')