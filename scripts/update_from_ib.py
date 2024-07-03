import os
from zipfile import ZipFile
from datetime import datetime, timedelta
from ib_insync import *

from dotenv import load_dotenv
load_dotenv(override=True)

multicharts_log_dir = os.getenv('MC_LOG_DIR') + '/TradingServer/'


def logtime_to_ts(str):
  return datetime.strptime(str, '%d.%m.%Y/%H:%M:%S.%f').timestamp()

def _getKeyValue(content, key):
  key_idx = content.find(key)
  if key_idx == -1:
    return ''
  value_idx = key_idx + len(key) + 1
  value_end_idx = content.find(';', value_idx)
  return content[value_idx:value_end_idx]

def get_trading_server_logs():
  logdir = os.path.join(multicharts_log_dir)
  logfiles = [f for f in os.listdir(logdir) if f.startswith('TradingServer')]
  def logfiles_trade(file):
    return os.path.getmtime(logdir + file)
  logfiles.sort(key=logfiles_trade)
  return [logdir + f for f in logfiles]


def get_logentry_ts_and_content(line):
  content_idx = line.find(' ')
  if content_idx == -1:
    return [None, None]
  line_split = line[:content_idx].split('-')
  if len(line_split) >= 3 and len(line_split[2]) == 23: 
    content = line[content_idx+1:].strip()
    log_ts = logtime_to_ts(line_split[2])
    return [log_ts, content]
  return [None, None]

def is_strategy_identifier(content):
  columns = content.split(';')
  return len(columns) > 50 and '@' in columns[2]

def is_order_event(content):
  columns = content.split(' ')
  return len(columns) > 0 and ('PDS' in columns[0] or 'CProfile::OnOrder' in columns[0] or 'CProfile::OnTrade' in columns[0])  

def get_strategy_mapping():
  strat_map = {}
  log_filepaths = get_trading_server_logs()
  for log_file in log_filepaths:
    print('Processing', log_file)
    extension = log_file.split('.')[-1]
    if extension == 'txt':
      with open(log_file, 'r') as f:
        for line in f:
          logentry_ts, content = get_logentry_ts_and_content(line)
          if logentry_ts == None or content == None:
            continue
          if is_strategy_identifier(content):
            cols = content.split(';')
            strategy_id = cols[1]
            broker_profile = cols[41][1:-1]
            account_id = cols[42][1:-1]
            workspace = cols[43][1:-1]
            strategy_name = cols[44][1:-1]
            if account_id not in strat_map.keys():
              strat_map[account_id] = {}
            strat_map[account_id][strategy_id] = {
              'broker_profile': broker_profile,
              'workspace': workspace,
              'strategy_name': strategy_name
            }
    elif extension == 'zip':
      with ZipFile(log_file) as zipfile:
        namelist = zipfile.namelist()
        with zipfile.open(namelist[0], 'r') as f:
          for line in f:
            logentry_ts, content = get_logentry_ts_and_content(line.decode('utf-8'))
            if logentry_ts == None or content == None:
              continue
            if is_strategy_identifier(content):
              cols = content.split(';')
              strategy_id = cols[1]
              broker_profile = cols[41][1:-1]
              account_id = cols[42][1:-1]
              workspace = cols[43][1:-1]
              strategy_name = cols[44][1:-1] if cols[44][-1] == '"' else cols[44][1:]
              if account_id not in strat_map.keys():
                strat_map[account_id] = {}
              strat_map[account_id][strategy_id] = {
                'broker_profile': broker_profile,
                'workspace': workspace,
                'strategy_name': strategy_name
              }
              print('    Register strategy:', account_id, strategy_id, strat_map[account_id][strategy_id])
              for elTraderId, strategy in strat_map[account_id].items():
                print('       ', elTraderId, strategy['strategy_name'])
  return strat_map

def get_trade_mapping():
  trade_map = {}
  log_filepaths = get_trading_server_logs()
  latest_log = ''
  last_modified = 0
  for logf in log_filepaths:
    extension = logf.split('.')[-1]
    t_modified = os.path.getmtime(logf)
    if t_modified > last_modified and extension == 'txt':
      last_modified = t_modified
      latest_log = logf

  with open(latest_log, 'r') as f:
    for line in f:
      logentry_ts, content = get_logentry_ts_and_content(line)
      if logentry_ts == None or content == None:
        continue
      if is_order_event(content):
        broker_id = _getKeyValue(content, 'BrIDStr')
        strategy_id = _getKeyValue(content, 'ELTraderID')
        account_id = _getKeyValue(content, 'Account')
        if account_id not in trade_map.keys():
          trade_map[account_id] = {}
        trade_map[account_id][broker_id] = strategy_id
  return trade_map

def connect(instance='paper'):
    ib = IB()
    ib.connect('127.0.0.1', 4001 if instance == 'live' else 4002, clientId=3)
    return ib
            
def update_from_ib(instance):
  strat_map = get_strategy_mapping()
  trade_map = get_trade_mapping()
  ib = connect(instance)
  print("Connected to IB")
  fills = ib.fills()
  print("Retrieved", len(fills), "fills")
  for fill in fills:
    account_id = fill.execution.acctNumber
    trade_id = fill.execution.orderRef.split(']')[0][17:]
    print("Fill:", trade_id, trade_map[account_id][trade_id], account_id, fill.commissionReport.realizedPNL)
    if trade_id and trade_id in trade_map[account_id].keys():
      strategy_id = trade_map[account_id][trade_id]
      #if strategy_id in strat_map[account_id].keys():
      strategy = strat_map[account_id][strategy_id]
      #print(fill.execution.time, account_id, fill.contract.symbol, fill.execution.acctNumber, fill.execution.side, fill.execution.shares, fill.execution.tradeRef[17:21], fill.commissionReport.realizedPNL)
      #print("  ", strategy['broker_profile'], strategy['workspace'], strategy['strategy_name'])
      print(f'{fill.execution.time} TradeId: {account_id}_{trade_id}; Wksp: {strategy["workspace"]}; Strat: {strategy["strategy_name"]}; Side: {fill.execution.side}; Qty: {fill.execution.shares}; PnL: {fill.commissionReport.realizedPNL}')
  
  ib.disconnect()

if __name__ == '__main__':
  update_from_ib()