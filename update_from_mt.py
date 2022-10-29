
import json
from time import sleep
from os import getenv
from datetime import datetime, timedelta
from dotenv import load_dotenv

from mt_connector.connector import mt_connector_client
import back.db as db
from back.utils import update_strategy_run_demo_kpis


load_dotenv()

LOOKBACK_DAYS_TO_UPDATE = 365

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
    balance = [1000]
    for order_id in order_ids:
        # trades_dict[order_id]['order_id'] = order_id
        # trades_list.append(trades_dict[order_id])
        mt_trade = trades_dict[order_id]
        balance.append(balance[-1] + mt_trade['pnl'])
        trade = db.Trade(
            f"{order_id}_{mt_trade['magic']}_D",
            f"{mt_trade['magic']}_D",
            mt_trade['symbol'],
            mt_trade['type'][0].upper() + mt_trade['type'][1:],
            mt_trade['open_time'].replace('.', '-'),
            mt_trade['close_time'].replace('.', '-'),
            mt_trade['open_price'],
            mt_trade['close_price'],
            mt_trade['lots'],
            mt_trade['pnl'],
            mt_trade['comment'].replace('[', '').replace(']', ''),
            mt_trade['comment'],
            mt_trade['TP'],
            mt_trade['SL'],
            mt_trade['commission'],
            mt_trade['swap']
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
        trades = mt_to_db_format(mt_trades_dict)
        print(' ****** MT TRADES ****** ')
        print('Magics of the trades retrieved:', trades.keys())
        print('Trades of magic 0:')
        for trade in trades[0]:
            print('*** ', trade)


        # db_cnx = db.get_connection()
        # db_strategies = db.get_demo_trades(db_cnx)
        # print(' ***** DB TRADES ***** ')
        # print('        Trades: ', db_strategies)


        # db_strategies = db.get_strategies()
        """
        updated_trades = {}
        updated_kpis = {}
        for db_strategy in db_strategies:
            magic = db_strategy['magic']
            db_trades = db.get_strategys_demo_trades(magic)
            start = datetime.strptime(db_trades[0]['openTime'][:10], '%Y-%m-%d') - timedelta(days=1)
            if db_trades:
                db_trades = [t for t in db_trades if t['closeTime'] != None] # shouldn't need to, but filtering out open positions
                if not db_trades:
                    db_trades = []
                print('Updating trades for strategy with magic ', magic)
                # print('  Number of DB trades: ', len(db_trades))
                db_order_ids = [trade['orderId'] for trade in db_trades]
                mt_magic_trades = mt_trades[magic] if magic in mt_trades else []
                # print('  Number of MT trades: ', len(mt_magic_trades))
                if len(mt_magic_trades):
                    new_trades = [trade for trade in mt_magic_trades if trade['orderId'] not in db_order_ids]
                else:
                    new_trades = []
                print('  Number of new trades to add: ', len(new_trades))
                db_trades.extend(new_trades)
                print('  Total trades (old and new): ', len(db_trades))
                updated_trades[magic] = db_trades
            elif magic in mt_trades:
                mt_magic_trades = [t for t in mt_trades[magic] if t['closeTime'] != None] # filter out open positions
                updated_trades[magic] = mt_magic_trades
            else:
                updated_trades[magic] = []
            # print(' ***** Updated trades for magic ', magic)
            # print(updated_trades[magic])
            updated_kpis[magic] = get_demo_kpis(start, updated_trades[magic])
            # print(' ***** KPIs for magic ', magic)
            # print(updated_kpis[magic])
        # print(' ***** UPDATED TRADES ***** ')
        # print('        Trades: ', updated_trades)
        """

        # SAVE TO DB
        # With mt trades insert all trades into db for each strategy
        # ignoring duplicate key errors (if they already exist, as this is expected)
        for magic in trades.keys():
            num_trades_added = 0
            for trade in trades[magic]:
                try:
                    db.save_trade(trade)
                    num_trades_added += 1
                except Exception as e:
                    if 'Duplicate entry' not in repr(e):
                        raise Exception(e)
            if num_trades_added > 0:
                print('For magic', magic, 'added', num_trades_added, 'trades')
                with open('../crontab.log', 'a') as f:
                        f.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' Num trades added for magic ' + magic + ': ' + str(num_trades_added) + "\n")
                update_strategy_run_demo_kpis(magic)
        # db.update_demo_data(db_cnx, updated_trades, updated_kpis)
        db.register_update('Success')

        self.connector.ACTIVE = False


MT4_files_dir = getenv('MT_FILES_DIR')

processor = read_and_save_trades(MT4_files_dir)

while processor.connector.ACTIVE:
    sleep(1)

