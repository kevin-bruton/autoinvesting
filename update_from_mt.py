
import json
from time import sleep
from os import getenv
from datetime import datetime, timedelta
from dotenv import load_dotenv

from mt_connector.connector import mt_connector_client
import back.db as db
from back.db import Trade
from back.utils import update_strategy_run_demo_kpis


load_dotenv()

LOOKBACK_DAYS_TO_UPDATE = 365

deleted_strategies = ['220612018']

def old_to_new_magic(trades_dict):
    olds = [-1254131479,-1254133479,-1254134479,-1254224457,-1254224458,-1254224459,-1254224460,-1254224461,-1254224462,-1254224463,-1254224464,-1254224465,-1254224466,-1254224467,-1254224468,-1254224469,-1254224470,-1254224471,-1254224472,-1254224473,-1254224474,-1254224475,-1254224476,-1254224478,20220604,202206101,202206103,2205141,2205142,2205144,2205145]
    news = [220705001,220703001,220702001,220612023,220612022,220612021,220612020,220612019,220612018,220612017,220612016,220612015,220612014,220612013,220612012,220612011,220612010,220612009,220612008,220612007,220612006,220612005,220612004,220612002,220604001,220610001,220610003,220514001,220514002,220514004,220514005]
    for order_id in trades_dict.keys():
        t = trades_dict[order_id]
        mt_magic = t['magic']
        try:
            idx = olds.index(mt_magic)
            trades_dict[order_id]['magic'] = news[idx]
        except:
            pass
    return trades_dict

def mt_to_db_format(trades_dict):
    trades_dict = old_to_new_magic(trades_dict)
    trades_by_magic = {}
    order_ids = trades_dict.keys()
    for order_id in order_ids:
        # trades_dict[order_id]['order_id'] = order_id
        # trades_list.append(trades_dict[order_id])
        mt_trade = trades_dict[order_id]
        account_id = f"{mt_trade['magic']}_D"
        trade = Trade(
            f"{order_id}_{account_id}",
            None, # masterOrderId
            account_id,
            mt_trade['magic'],
            mt_trade['symbol'],
            mt_trade['type'][0].upper() + mt_trade['type'][1:],
            mt_trade['open_time'].replace('.', '-'),
            mt_trade['close_time'].replace('.', '-'),
            mt_trade['open_price'],
            mt_trade['close_price'],
            mt_trade['lots'],
            mt_trade['pnl'],
            None, # balance
            mt_trade['comment'].replace('[', '').replace(']', ''),
            mt_trade['comment'],
            mt_trade['SL'],
            mt_trade['TP'],
            mt_trade['swap'],
            mt_trade['commission']
        )
        if trade.orderType == 'Unknown':
            continue

        if mt_trade['magic'] not in trades_by_magic:
            trades_by_magic[mt_trade['magic']] = [trade]
        else:
            trades_by_magic[mt_trade['magic']].append(trade)
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
    
    def on_order_event(self, order_event, order, modified_fields=None):
        # print('on_order_event:', order_event, '; order:', order)
        pass

    def on_historic_trades(self):
        print(' ***** RECEIVED HISTORIC DATA ***** ')
        mt_trades_dict = self.connector.historic_trades
        trades_by_magic = mt_to_db_format(mt_trades_dict)
        print(' ****** MT TRADES ****** ')
        print('Magics of the trades retrieved:', trades_by_magic.keys())

        # SAVE TO DB
        # With mt trades insert all trades into db for each strategy
        # ignoring duplicate key errors (if they already exist, as this is expected)
        already_existing_trades = 0
        for magic in trades_by_magic.keys():
            if str(magic) in deleted_strategies:
                continue
            num_trades_added = 0
            for trade in trades_by_magic[magic]:
                try:
                    if trade.orderType in ['Buy', 'Sell']:
                        db.save_trade(trade)
                        num_trades_added += 1
                except Exception as e:
                    if 'Duplicate entry' not in repr(e):
                        raise Exception(e)
                    else:
                        already_existing_trades += 1
            if num_trades_added > 0:
                print('For magic', magic, 'added', num_trades_added, 'trades')
                with open('../crontab.log', 'a') as f:
                        f.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' Num trades added for magic ' + str(magic) + ': ' + str(num_trades_added) + "\n")
                update_strategy_run_demo_kpis(magic)
        db.register_update('Success')
        print('Number of trades not added because they were already in the DB:', already_existing_trades)

        self.connector.ACTIVE = False


MT4_files_dir = getenv('MT_FILES_DIR')

processor = read_and_save_trades(MT4_files_dir)

while processor.connector.ACTIVE:
    sleep(1)

