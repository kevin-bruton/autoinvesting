from time import sleep
from os import getenv
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv(override=True)

#from db2.accounts import update_kpis
import db
from db.updates import register_update
from mt_connector.connector import mt_connector_client
from db.trades import Trade, get_strategys_demo_trades, save_trade
from fast.utils import get_demo_kpis

LOOKBACK_DAYS_TO_UPDATE = 365

datetime_fmt = '%Y-%m-%d %H:%M:%S'
deleted_strategies = ['220612018', '-1254135478', '-1254135477', '220804002']

def old_to_new_magic(magic):
  olds = [-1254135479,-1254131479,-1254133479,-1254134479,-1254224457,-1254224458,-1254224459,-1254224460,-1254224461,-1254224462,-1254224463,-1254224464,-1254224465,-1254224466,-1254224467,-1254224468,-1254224469,-1254224470,-1254224471,-1254224472,-1254224473,-1254224474,-1254224475,-1254224476,-1254224478,20220604,202206101,202206103,2205141,2205142,2205144,2205145,11111,221292001]
  news = [  220701001,  220705001,220703001,220702001,220612023,220612022,220612021,220612020,220612019,220612018,220612017,220612016,220612015,220612014,220612013,220612012,220612011,220612010,220612009,220612008,220612007,220612006,220612005,220612004,220612002,220604001,220610001,220610003,220514001,220514002,220514004,220514005,221101004,221229001]
  try: 
      idx = olds.index(magic)
      magic = news[idx]
  except:
      pass
  return magic

def old_to_new_magic_in_trades(trades_dict):
  for order_id in trades_dict.keys():
    t = trades_dict[order_id]
    mt_magic = t['magic']
    trades_dict[order_id]['magic'] = old_to_new_magic(mt_magic)
  return trades_dict

def mt_to_db_format(trades_dict, balance):
    trades_dict = old_to_new_magic_in_trades(trades_dict)
    trades_by_magic = {}
    order_ids = trades_dict.keys()
    for order_id in order_ids:
        # trades_dict[order_id]['order_id'] = order_id
        # trades_list.append(trades_dict[order_id])
        mt_trade = trades_dict[order_id]
        #account_id = f"{mt_trade['magic']}_D"
        strategyRunId = db.get_trade_strategyrun_id(str(mt_trade['magic']), 'paper')
        trade = Trade(
            orderId=f"{order_id}_{strategyRunId}",
            strategyRunId=strategyRunId,
            symbol=mt_trade['symbol'],
            orderType=mt_trade['type'][0].upper() + mt_trade['type'][1:],
            openTime=mt_trade['open_time'].replace('.', '-'),
            closeTime=mt_trade['close_time'].replace('.', '-'),
            openPrice=mt_trade['open_price'],
            closePrice=mt_trade['close_price'],
            size=mt_trade['lots'],
            profit=mt_trade['pnl'],
            balance=balance,
            closeType=mt_trade['comment'].replace('[', '').replace(']', ''),
            comment=mt_trade['comment'],
            sl=mt_trade['SL'],
            tp=mt_trade['TP'],
            swap=mt_trade['swap'],
            commission=mt_trade['commission']
        )
        if trade.orderType == 'Unknown':
            continue

        if mt_trade['magic'] not in trades_by_magic:
            trades_by_magic[mt_trade['magic']] = [trade]
        else:
            trades_by_magic[mt_trade['magic']].append(trade)
    return trades_by_magic

""" def update_strategy_run_demo_kpis (magic):
  # get start, deposit, trades
  deposit = 1000
  trades = get_strategys_demo_trades(magic)
  if len(trades):
    start_date =  datetime.strptime(trades[0]['openTime'],datetime_fmt) - timedelta(days=1)
    kpis = get_demo_kpis(start_date, trades, deposit)
    update_kpis(f"{magic}_D", start_date, deposit, tuple(kpis.values()))
 """

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
        #print("Account info:", self.connector.account_info)

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
        #print(' ***** RECEIVED HISTORIC DATA ***** ')
        mt_trades_dict = self.connector.historic_trades
        trades_by_magic = mt_to_db_format(mt_trades_dict, self.connector.account_info['balance'])
        #print(' ****** MT TRADES ****** ')
        #print('Magics of the trades retrieved:', trades_by_magic.keys())

        # SAVE TO DB
        # With mt trades insert all trades into db for each strategy
        # ignoring duplicate key errors (if they already exist, as this is expected)
        already_existing_trades = 0
        num_trades_added = 0
        for magic in trades_by_magic.keys():
            if str(magic) in deleted_strategies:
                continue
            for trade in trades_by_magic[magic]:
                try:
                    if trade.orderType in ['Buy', 'Sell']:
                        save_trade(trade)
                        num_trades_added += 1
                except Exception as e:
                    if 'UNIQUE constraint failed' not in repr(e):
                        print("Error saving trade:", repr(e), "; TRADE: ", trade)
                        # raise Exception(e)
                    else:
                        already_existing_trades += 1
            if num_trades_added > 0:
                #print('For magic', magic, 'added', num_trades_added, 'trades')
                with open('../crontab.log', 'a') as f:
                        f.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' Num trades added for magic ' + str(magic) + ': ' + str(num_trades_added) + "\n")
                #update_strategy_run_demo_kpis(magic)
        register_update('Success')
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ': Update from MT. Number of trades added: ' + str(num_trades_added) + '; Already existing: ' + str(already_existing_trades))

        self.connector.ACTIVE = False

def run_update_from_mt():
    with open('logs/update_from_mt.log', 'a') as f:
        f.write(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' Starting update from MT4\n')

    metatrader_files_dir = getenv('MT_DEMO_FILES_DIR')
    #print('Metatrader files directory:', metatrader_files_dir)
    processor = read_and_save_trades(metatrader_files_dir)

    while processor.connector.ACTIVE:
        sleep(1)

if __name__ == '__main__':
    run_update_from_mt()