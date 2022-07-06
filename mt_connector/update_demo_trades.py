
import json
from runpy import _ModifiedArgv0
from time import sleep
from threading import Thread
from os.path import join, exists
from traceback import print_exc
from random import random
from datetime import datetime, timedelta
from dotenv import load_dotenv

from connector import mt_connector_client
import db
from kpis import get_kpis

load_dotenv()

LOOKBACK_DAYS_TO_UPDATE = 10

def mt_to_db_format(trades_dict):
    trades_by_magic = {}
    order_ids = trades_dict.keys()
    balance = [1000]
    for order_id in order_ids:
        # trades_dict[order_id]['order_id'] = order_id
        # trades_list.append(trades_dict[order_id])
        t = trades_dict[order_id]
        balance.append(balance[-1] + t['pnl'])
        trade = {
            'orderId': order_id,
            'magic': t['magic'],
            'symbol': t['symbol'],
            'direction': t['type'][0].upper() + t['type'][1:],
            'openTime': t['open_time'],
            'openPrice': t['open_price'],
            'closeTime': t['close_time'],
            'closePrice': t['close_price'],
            'size': t['lots'],
            'profit': t['pnl'],
            'balance': balance[-1],
            'closeType': t['comment'].replace('[', '').replace(']', ''),
            'comment': t['comment'],
            'tp': t['TP'],
            'sl': t['SL'],
            'commission': t['commission'],
            'swap': t['swap']
        }

        if trade['magic'] not in trades_by_magic:
            trades_by_magic[trade['magic']] = [trade]
        else:
            trades_by_magic[trade['magic']].append(trade)
    return trades_by_magic

def str_to_db_format(tradesStr):
    trades_by_magic = {}
    tradesJson = json.loads(tradesStr)
    for strategy in tradesJson:
        trades_by_magic[strategy['magic']] = strategy['demoTrades']
    return trades_by_magic


class read_and_save_trades():

    def __init__(self, MT4_directory_path, 
                 sleep_delay=0.005,             # 5 ms for time.sleep()
                 max_retry_command_seconds=10,  # retry to send the commend for 10 seconds if not successful. 
                 verbose=False
                 ):

        self.last_open_time = datetime.utcnow()
        self.last_modification_time = datetime.utcnow()

        self.connector = mt_connector_client(self, MT4_directory_path, sleep_delay, 
                              max_retry_command_seconds, verbose=verbose)
        sleep(1)

        self.connector.start()
        
        # account information is stored in self.connector.account_info.
        print("Account info:", self.connector.account_info)

        self.connector.get_historic_trades(lookback_days=LOOKBACK_DAYS_TO_UPDATE)

    def on_message(self, message):
        pass
        """ print(' ***** RECEIVED MESSAGE ****** ')
        print('       ', message)
        if message['message'] == 'Successfully read historic trades.':
            print('       Trades: ', self.connector.historic_trades) """

    def on_historic_trades(self):
        print(' ***** RECEIVED HISTORIC DATA ***** ')
        mt_trades_dict = self.connector.historic_trades
        mt_trades = mt_to_db_format(mt_trades_dict)
        print(' ****** MT TRADES ****** ')
        print(mt_trades)

        db_cnx = db.get_connection()
        db_strategies = db.get_demo_trades(db_cnx)
        # print(' ***** DB TRADES ***** ')
        # print('        Trades: ', db_strategies)

        updated_trades = {}
        updated_kpis = {}
        for db_strategy in db_strategies:
            magic = db_strategy['magic']
            start = db_strategy['demoStart']
            db_trades = db_strategy['demoTrades']
            if db_trades:
                db_trades = json.loads(db_trades)
                # print('TRADES FOR MAGIC ', magic, ': ', db_trades)
                db_order_ids = [trade['orderId'] for trade in db_trades]
                mt_magic_trades = mt_trades[magic] if magic in mt_trades else []
                if len(mt_magic_trades):
                    new_trades = [trade for trade in mt_magic_trades if trade['orderId'] not in db_order_ids]
                else:
                    new_trades = []
                # print('*************** NEW TRADES: ', new_trades)
                db_trades.extend(new_trades)
                updated_trades[magic] = db_trades
            elif magic in mt_trades:
                updated_trades[magic] = mt_trades[magic]
            else:
                updated_trades[magic] = []
            print(' ***** Updated trades for magic ', magic)
            print(updated_trades[magic])
            updated_kpis[magic] = get_kpis(start, updated_trades[magic])
            print(' ***** KPIs for magic ', magic)
            print(updated_kpis[magic])
        print(' ***** UPDATED TRADES ***** ')
        print('        Trades: ', updated_trades)

        # SAVE TO DB
        db.update_demo_data(db_cnx, updated_trades, updated_kpis)

        db_cnx.close()
        self.connector.ACTIVE = False

        """ print('       Symbol: ', symbol)
        print('       Timeframe: ', timeframe)
        print('       Data: ', data) """


MT4_files_dir = '/Users/kevin/Library/Application Support/MetaTrader 4/Bottles/metatrader64/drive_c/Program Files (x86)/MetaTrader 4/MQL4/Files/'

processor = read_and_save_trades(MT4_files_dir)

while processor.connector.ACTIVE:
    sleep(1)

