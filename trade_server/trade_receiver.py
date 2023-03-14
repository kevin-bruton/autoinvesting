import json
from time import sleep
from os import getenv
from datetime import datetime, timedelta
from dotenv import load_dotenv

from mt_connector.connector import mt_connector_client

# from trade_server.db import add_trade_to_demo_trades
import back.db as db
from back.db import Trade, Order

load_dotenv()

LOOKBACK_DAYS_TO_UPDATE = 365

def log(msg):
  time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  with open(f"logs/master.log", 'a') as f:
    f.write(f"{time_str} {msg}\n")

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
        t = trades_dict[order_id]
        balance.append(balance[-1] + t['pnl'])
        get_close_type = lambda c: c[c.find('[')+1:c.find(']')] if c.find('[') != -1 else ''
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
            'closeType': get_close_type(t['comment']),
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


class TradeReceiver():

    def __init__(self,
                  MT4_directory_path,            
                  received_trade_cb,             # Received trade callback
                  sleep_delay=0.5,             # 0.005 == 5 ms for time.sleep()
                  max_retry_command_seconds=10,  # retry to send the commend for 10 seconds if not successful. 
                  verbose=False
                ):
        self.received_trade_cb = received_trade_cb

        self.connector = mt_connector_client(self, MT4_directory_path, sleep_delay, 
                              max_retry_command_seconds, verbose=verbose)
        sleep(1)

        self.connector.start()
        
        # account information is stored in self.connector.account_info.
        print("[RECEIVER] Receiving trades from this account:", self.connector.account_info)

    def on_message(self, message):
        print('[RECEIVER] on_message:', message)
        pass
        """ print(' ***** RECEIVED MESSAGE ****** ')
        print('       ', message)
        if message['message'] == 'Successfully read historic trades.':
            print('       Trades: ', self.connector.historic_trades) """
    
    def on_order_event(self, order_event, order, modified_fields=None):
        self.received_trade_cb(order_event, order, modified_fields)

def run_receiver (trade_queue):
  def on_order_event(event, mt_order, modified_fields):
    print('[RECEIVER]', f"ORDER EVENT={event.upper()}:", mt_order, '; modified_fields:', modified_fields)
    if event == 'order_created':    handle_order_created(trade_queue, mt_order)
    if event == 'modified':         handle_order_modified(trade_queue, mt_order, modified_fields)
    if event == 'order_removed':    handle_order_removed(trade_queue, mt_order)

  print('[RECEIVER] Waiting to receive trades...')
  tradeReceiver = TradeReceiver(getenv('MT_FILES_DIR'), on_order_event)

  while tradeReceiver.connector.ACTIVE:
    sleep(1)
    # print('Trade receiver running...')
def handle_order_created (trade_queue, mt_order):
  if mt_order['direction'] in ['Buylimit','Buystop','Selllimit','Sellstop','Buy','Sell']:
    mt_order['action'] = 'place_order'
    status = 'open' if mt_order['direction'] in ['Buy', 'Sell'] else 'placed'
    order = Order(mt_order['orderId'], None, f"{mt_order['magic']}_D", mt_order['magic'], mt_order['symbol'], mt_order['direction'], mt_order['openTime'], mt_order['openPrice'], mt_order['size'], mt_order['comment'], mt_order['sl'], mt_order['tp'], status)
    db.save_order(order)
    if status == 'open':
      log(f"POSITION OPENED: {order}")
    else:
      log(f"ORDER CREATED: {order}")
    trade_queue.put(mt_order)

def handle_order_modified (trade_queue, mt_order, modified_fields):
  mt_order['action'] = 'modify'
  log(f"ORDER MODIFIED: {mt_order}")
  trade_queue.put(mt_order)

def handle_order_removed (trade_queue, mt_order):
  if mt_order['direction'] in ['Buy','Sell'] and mt_order['closeTime']: # Position closed -> save to DB
    mt_order['action'] = 'close_position'
    print('[RECEIVER] POSITION CLOSED: ', mt_order)
    db.delete_order(mt_order['orderId'])
    trade = Trade(mt_order['orderId'],None,f"{mt_order['magic']}_D",mt_order['magic'],mt_order['symbol'],mt_order['direction'],mt_order['openTime'],mt_order['closeTime'],mt_order['openPrice'],mt_order['closePrice'],mt_order['size'],mt_order['profit'],mt_order['balance'],mt_order['closeType'],mt_order['comment'],mt_order['sl'],mt_order['tp'],mt_order['swap'],mt_order['commission'])
    db.save_trade(trade)
    log(f"POSITION CLOSED: {trade}")
    if not mt_order['sl'] and not mt_order['tp']: # Only make client's close their corresponding order if they don't have a SL and TP
       trade_queue.put(mt_order)
  elif mt_order['direction'] in ['Buylimit', 'Buystop', 'Selllimit', 'Sellstop']:
    mt_order['action'] = 'cancel_order'
    print('[RECEIVER] ORDER CANCELLED: ', mt_order)
    db.update_order_status(mt_order['orderId'], 'cancelled')
    log(f"ORDER CANCELLED: {mt_order}")
    trade_queue.put(mt_order)

