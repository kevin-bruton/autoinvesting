import os
from zipfile import ZipFile
from datetime import datetime

from db.updates import get_mc_logfile_entry_read_ts, get_mc_logfile_modified_ts, register_mc_logfile_entry_read_ts, register_mc_logfile_modified_ts
from fast.routers.send_sse import send_sse
from mc.log_analysis.process_logentry import processLogentry, getOrders, getStrategies

# from db.orders import get_last_filled_order_id, save_log_orders, get_order
# from db.positions import save_positions
# from db.strategies import save_strategies, \
#   get_strategy_by_el_trader_id as db_get_strategy_by_el_trader_id
#   # get_strategy_by_trader_id as db_get_strategy_by_trader_id, \
# from db.timestamps import get_timestamp, save_timestamp
# from utils.config import get_config_value
# from utils.telegram import send_position_message

def ts_to_str(ts):
  return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')

def logtime_to_ts(str):
  return datetime.strptime(str, '%d.%m.%Y/%H:%M:%S.%f').timestamp()
"""
def logfile_not_modified_since_last_read(logfile_modified_ts):
  last_read = get_timestamp('last_trading_server_logfile_modification')
  if last_read == None:
    last_read = 0
  if last_read == logfile_modified_ts:
    print('TradingServer logfile has not been modified since last chec. Last:', last_read, '\n')
    return True
  save_timestamp(logfile_modified_ts, 'last_trading_server_logfile_modification')
  return False
"""
def get_all_logfile_names():
  logdir = os.path.join(os.getenv('MC_LOG_DIR'), 'TradingServer/')
  logfiles = [f for f in os.listdir(logdir) if f.startswith('TradingServer')]
  def logfiles_order(file):
    return os.path.getmtime(logdir + file)
  logfiles.sort(key=logfiles_order)
  return [logdir + f for f in logfiles]
"""
def get_latest_logfilepath():
  dev_logfiles = get_config_value('dev_logfiles')
  if dev_logfiles:
    logdir = os.path.join(get_config_value('root_dir'), 'cron/')
    logfiles = ['TradingServer_2C28_11304_Trace0.txt']
  else:
    logdir = os.path.join(get_config_value('multicharts_data_directory'), 'Logs/TradingServer/')
    logfiles = [f for f in os.listdir(logdir) if f.startswith('TradingServer')]
  if len(logfiles) == 0:
    return
  last_modified = 0
  
  # Get the latest trading server log file name (as there may be more than one)
  logfile = ''
  for logf in logfiles:
    t_modified = os.path.getmtime(logdir + logf)
    if t_modified > last_modified:
      last_modified = t_modified
      logfile = logf
  return [logdir + logfile, last_modified]
"""

def logentry_already_processed(logentry_ts, last_read_log_entry_ts):
  return last_read_log_entry_ts and logentry_ts < last_read_log_entry_ts

def get_logentry_ts_and_content(line):
  content_idx = line.find(' ')
  if content_idx == -1:
    return [None, None]
  line_split = line[:content_idx].split('-')
  if len(line_split) >= 3 and len(line_split[2]) == 23: 
    content = line[content_idx+1:].strip()
    log_ts = ts_to_str(logtime_to_ts(line_split[2]))
    return [log_ts, content]
  return [None, None]
"""
def read_all_logs():
  last_entry_ts = 0
  logfilepaths = get_all_logfile_names()
  for logfilepath in logfilepaths:
    print('Processing', logfilepath)
    extension = logfilepath.split('.')[-1]
    if extension == 'zip':
      with ZipFile(logfilepath) as zipfile:
        namelist = zipfile.namelist()
        with zipfile.open(namelist[0], 'r') as f:
          for line in f:
            logentry_ts, content = get_logentry_ts_and_content(line.decode('utf-8'))
            if logentry_ts == None or content == None:
              continue

            if logentry_already_processed(logentry_ts, last_entry_ts):
              continue

            #print(ts_to_str(logentry_ts)[:16], ts_to_str(last_read_log_entry_ts)[:16])
            if last_entry_ts and ts_to_str(logentry_ts)[:13] != ts_to_str(last_entry_ts)[:13]:
              print('  Reading log entries at hour: ', ts_to_str(logentry_ts)[:13])
            processLogentry(logentry_ts, content)
            last_entry_ts = logentry_ts
    else:
      with open(logfilepath, 'r') as f:
        for line in f:
          logentry_ts, content = get_logentry_ts_and_content(line)
          if logentry_ts == None or content == None:
            continue

          if logentry_already_processed(logentry_ts, last_entry_ts):
            continue

          #print(ts_to_str(logentry_ts)[:16], ts_to_str(last_read_log_entry_ts)[:16])
          if last_entry_ts and ts_to_str(logentry_ts)[:13] != ts_to_str(last_entry_ts)[:13]:
            print('  Reading log entries at hour: ', ts_to_str(logentry_ts)[:13])
          processLogentry(logentry_ts, content)
          last_entry_ts = logentry_ts

  save_timestamp(last_entry_ts, 'last_trading_server_log_read')
  print('  Finished processing Trading Server logs at', datetime.now())
  orders = getOrders()
  strategies = getStrategies()
  print('  read_all_logs saving ', len(orders), 'orders and', len(strategies), 'strategies to the database...')
  strategies_inserted = save_strategies(strategies)
  orders_inserted = save_log_orders(orders)
  print('  Inserted/updated', strategies_inserted, 'strategies,', orders_inserted, 'orders\n')
        
def read_latest_log():
  try:
    logfile, logfile_modified_ts = get_latest_logfilepath()
  except Exception as e:
    print('Error: could not read TradingServer log', e, '\n')
    return
  if logfile_not_modified_since_last_read(logfile_modified_ts):
    return
  
  print("\nReading latest log file:", logfile, '...')
  with open(logfile, 'r') as f:
    #global last_filled_order_id
    last_entry_ts = get_timestamp('last_trading_server_log_read')
    #last_filled_order_id = get_last_filled_order_id()

    # Read log entries
    print('\nReading latest log file:\n', logfile,'\nUpdating orders and positions at', datetime.now(), '...')
    for line in f:
      logentry_ts, content = get_logentry_ts_and_content(line)
      if logentry_ts == None or content == None:
        continue

      if logentry_already_processed(logentry_ts, last_entry_ts):
        continue

      #print(ts_to_str(logentry_ts)[:16], ts_to_str(last_read_log_entry_ts)[:16])
      if last_entry_ts and ts_to_str(logentry_ts)[:13] != ts_to_str(last_entry_ts)[:13]:
        print('  Reading log entries at hour: ', ts_to_str(logentry_ts)[:13])
      processLogentry(logentry_ts, content)
      last_entry_ts = logentry_ts

    save_timestamp(last_entry_ts, 'last_trading_server_log_read')
    print('  Finished processing Trading Server logs at', datetime.now())
    orders = getOrders()
    strategies = getStrategies()
    print('  read_latest_log saving ', len(orders), 'orders and', len(strategies), 'strategies to the database...')
    print('  first order:', orders[0] if len(orders) > 0 else 'None')
    strategies_inserted = save_strategies(strategies)
    orders_inserted = save_log_orders(orders)
    print('     Inserted/updated', strategies_inserted, 'strategies,', orders_inserted, 'orders\n')
"""
def process_log_line(line, last_read_log_entry_ts):
  logentry_ts, content = get_logentry_ts_and_content(line)
  if logentry_ts == None or content == None:
    return last_read_log_entry_ts

  if logentry_ts < last_read_log_entry_ts:
    return last_read_log_entry_ts

  #print(ts_to_str(logentry_ts)[:16], ts_to_str(last_read_log_entry_ts)[:16])
  if logentry_ts[:13] != last_read_log_entry_ts[:13]:
    print('  Reading log entries at hour: ', logentry_ts[:13])
    send_sse('logprocessing', 'Reading log entries at hour: ' + logentry_ts[:13])
  processLogentry(logentry_ts, content)
  return logentry_ts


def process_last_logentries():
  logfilepaths = get_all_logfile_names() # files returned are ordered by modification time
  for logfilepath in logfilepaths:
    print('Processing', logfilepath)
    send_sse('logprocessing', 'Processing ' + logfilepath)
    logfile_modified_ts = ts_to_str(os.path.getmtime(logfilepath))
    prev_modified_logfile_ts = get_mc_logfile_modified_ts(logfilepath)
    if logfile_modified_ts > prev_modified_logfile_ts:
      last_entry_ts = get_mc_logfile_entry_read_ts(logfilepath)
      extension = logfilepath.split('.')[-1]
      if extension == 'zip':
        with ZipFile(logfilepath) as zipfile:
          namelist = zipfile.namelist()
          with zipfile.open(namelist[0], 'r') as f:
            for line in f:
              last_entry_ts = process_log_line(line.decode('utf-8'), last_entry_ts)
      else:
        with open(logfilepath, 'r') as f:
          for line in f:
            last_entry_ts = process_log_line(line, last_entry_ts)
      register_mc_logfile_modified_ts(logfilepath, logfile_modified_ts)
      register_mc_logfile_entry_read_ts(logfilepath, last_entry_ts)


  #register_mc_last_read_logfile(last_logfile['filename'], last_logfile['modified_ts'])
  #register_mc_last_read_logentry(last_entry_ts)

  #save_timestamp(last_entry_ts, 'last_trading_server_log_read')
  print('  Finished processing Trading Server logs at', datetime.now())
  send_sse('logprocessing', 'Finished processing Trading Server logs at ' + str(datetime.now()))
  # orders = getOrders()
  # strategies = getStrategies()
  # print('  read_all_logs saving ', len(orders), 'orders and', len(strategies), 'strategies to the database...')
  # strategies_inserted = save_strategies(strategies)
  # orders_inserted = save_log_orders(orders)
  # print('  Inserted/updated', strategies_inserted, 'strategies,', orders_inserted, 'orders\n')
        