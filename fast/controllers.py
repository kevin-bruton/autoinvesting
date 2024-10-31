from os import getenv, listdir, mkdir, path, remove
from shutil import copy2
from db.strategy_runs import StrategyRun, get_strategyrun_id, get_strategyrunid, get_strategyrunid_backtest, save_strategyrun
from db.strategies import get_strategy_tf_symbol
from fast.random_name import get_random_name
from db.strategies import Strategy, get_active_strategyruns, save_strategy, \
  decommission_strategy as decom_strategy, reactivate_strategy as react_strategy
from db.trades import Trade, get_strategys_backtest_trades, get_strategys_combined_trades, get_strategys_live_trades, get_strategys_oos_start, save_trade
from db.accounts import Account, get_mt_instance_dir_name, save_account
from fast.utils import get_bt_kpis, get_performance_metrics, get_project_root_dir, normalize_position_sizes, dec2
from datetime import datetime, timedelta
import pandas as pd
from scripts.create_templates import create_mt_templates

date_fmt = '%Y-%m-%d'
datetime_fmt = '%Y-%m-%d %H:%M:%S'

def save_new_strategies (upload_folder):
  folder = f"{get_project_root_dir()}/files/{upload_folder}"
  files = listdir(folder)
  csv_files = [f for f in files if f[-3:] == 'csv']
  deposit = 1000
  for filename in csv_files:
    base_filename = filename[:-4]
    symbol, timeframe, strategyId = base_filename.split('_')
    friendlyName = get_random_name()
    strategy = Strategy(strategyId, friendlyName)
    save_strategy(strategy)
    print('Saved strategy', friendlyName, base_filename)
    with open(f"{folder}/{filename}") as f:
      lines = [
        [d[1:-1] for d in l.split(';')]
        for l in f.read().splitlines()
      ]
      trades = [
        # If there is an error of duplicate trades while uploading:
        # Make sure that the csv of trades exported from SQX was done
        # including only trades from the Main backtest (options while exporting)
        Trade(
          orderId=f"{l[0]}_{strategyId}_B",
          symbol=symbol,
          orderType=l[2],
          openTime=l[3].replace('.', '-'),
          closeTime=l[6].replace('.', '-'),
          openPrice=float(l[4]),
          closePrice=float(l[7]),
          size=float(l[5]),
          profit=float(l[8]),
          balance=float(l[9]),
          closeType=l[11],
          comment=l[15]
        )
        for l in lines[1:]
        if l[7] and l[8]
      ]
      start_date = trades[0].openTime
      end_date = trades[-1].closeTime
      backtestStrategyRun = StrategyRun(strategyId, None, symbol, timeframe, 'backtest', start_date, end_date)
      save_strategyrun(backtestStrategyRun)
      for trade in trades:
        strategyRunId = get_strategyrun_id(strategyId, 'backtest')
        trade = trade._replace(strategyRunId=strategyRunId)
        save_trade(trade)
  return True


def get_account_logs (account_id):
  try:
    with open(f"logs/client-{account_id}.log", 'r') as f:
      log = f.read()
  except FileNotFoundError:
    return 'No logs found for this account'
  return log

def log(txt):
    with open("/home/admin/autoinvesting/back/correlation.log", "a") as f:
        f.write(txt + "\n")

def get_strategy_detail (strategyId, accountId):
  normalized_position_size = 1
  live_trades = normalize_position_sizes(get_strategys_live_trades(strategyId, accountId), normalized_position_size)
  timeframe, symbol = get_strategy_tf_symbol(strategyId)
  live_start = (live_trades[0]['closeTime'] - timedelta(days=1)) if live_trades else datetime.now().strftime('%Y-%m-%d')
  backtest_trades = normalize_position_sizes(get_strategys_backtest_trades(strategyId, up_until_date=live_start), normalized_position_size)
  oos_start = get_strategys_oos_start(strategyId)
  combined_trades = backtest_trades + live_trades
  capital, start_date, end_date, metrics = get_performance_metrics(backtest_trades)
  strategyRunId = get_strategyrunid_backtest(strategyId)
  backtest = {'strategyRunId': strategyRunId, 'startingBalance': capital, 'startDate': start_date, 'endDate': end_date, 'positionSize': live_trades[0]['size'], 'metrics': metrics, 'trades': backtest_trades}
  capital, start_date, end_date, metrics = get_performance_metrics(live_trades)
  strategyRunId = get_strategyrunid(strategyId, accountId)
  live = {'strategyRunId': strategyRunId, 'startingBalance': capital, 'startDate': start_date, 'endDate': end_date, 'positionSize': live_trades[0]['size'], 'metrics': metrics, 'trades': live_trades}
  capital, start_date, end_date, metrics = get_performance_metrics(combined_trades)
  combined = {'startingBalance': capital, 'startDate': start_date, 'endDate': end_date, 'positionSize': live_trades[0]['size'], 'metrics': metrics, 'trades': combined_trades}
  return {'backtest': backtest, 'live': live, 'combined': combined, 'oosStart': oos_start, 'timeframe': timeframe, 'symbol': symbol}

def get_strategies_summary (accountId):
  position_sizes_normalized = 1
  strategy_runs = get_active_strategyruns(accountId)
  strategy_runs = [dict(s) for s in strategy_runs]
  for strategy_run in strategy_runs:
    trades = normalize_position_sizes(get_strategys_live_trades(strategy_run['strategyId'], accountId), position_sizes_normalized)
    if trades:
      startingBalance, startDate, endDate, metrics = get_performance_metrics(trades)
      strategy_run['startingBalance'] = startingBalance
      strategy_run['startDate'] = startDate
      strategy_run['endDate'] = endDate
      strategy_run['metrics'] = metrics
    else:
      strategy_run['startingBalance'] = 0
      strategy_run['startDate'] = None
      strategy_run['endDate'] = None
      strategy_run['metrics'] = {}
  return strategy_runs

def get_portfolio_evaluation (data_type, account_id, strategy_ids):
  trades = []
  for strategy_id in strategy_ids:
    if data_type == 'backtest':
      strat_trades = get_strategys_backtest_trades(strategy_id)
    elif data_type == 'live':
      strat_trades = get_strategys_live_trades(strategy_id, account_id)
    elif data_type == 'combined':
      strat_trades = get_strategys_combined_trades(strategy_id, account_id)
    trades.extend(strat_trades)

  # Order all trades of the different strategies
  trades = sorted(trades, key=lambda t: t['closeTime'])
  # Adjust profits for a position size of 1 for all trades
  trades = normalize_position_sizes(trades)
  capital, start_date, end_date, metrics = get_performance_metrics(trades)
  print('Metrics:', metrics)
  for index, trade in enumerate(trades):
    trades[index] = {'closeTime': trade['closeTime'], 'profits': dec2(trade['balance'] - capital)}
  df = pd.DataFrame(trades)
  #df = df[['closeTime', 'profit']]
  df = df.groupby(by=pd.Grouper(key='closeTime', freq='W')).last(skipna=True).ffill()
  #df[strategyId] = df['profit'].cumsum().astype(float)
  return { 'capital': capital, 'startDate': start_date, 'endDate': end_date, 'metrics': metrics, 'chartData': df }

def calc_correlation_matrix (accountId, data_type, timeframe, strategyIds):
  """
    magic = list of integers
    data_type = 'live', 'backtest' or 'combined'
    timeframe has to be 'D', 'W' or 'M'
  """
  data = pd.DataFrame()
  for strategyId in strategyIds:
    if data_type == 'backtest':
      trades = get_strategys_backtest_trades(strategyId)
    elif data_type == 'live':
      trades = get_strategys_live_trades(strategyId, accountId)
    elif data_type == 'combined':
      trades = get_strategys_combined_trades(strategyId, accountId)
    for index, trade in enumerate(trades):
      trades[index] = {'closeTime': trade['closeTime'], 'profit': trade['profit']}
    df = pd.DataFrame(trades)
    #df = df[['closeTime', 'profit']]
    df = df.groupby(pd.Grouper(key='closeTime', freq=timeframe)).sum()
    df[strategyId] = df['profit'].cumsum().astype(float)
    # df['profit_'+str(magic)] = df['profit']
    df = df.drop(columns='profit')
    if data.empty:
      data = df
    else:
      data = pd.concat([data, df], axis=1, join='outer').fillna(0)
  correlation_json = data.corr()#.to_json(orient='columns')
  return correlation_json
  #return '{ "data": ' + correlation_json + '}'

def decommission_strategy (magic):
  decom_strategy(magic)

def reactivate_strategy (magic):
  react_strategy(magic)

def apply_position_sizing (account_id, pos_sizes):
  mt_files_account_ea_folder = f"{get_project_root_dir()}/files/{get_mt_instance_dir_name(account_id)}_eas_to_install/"
  src_folder = f"{get_project_root_dir()}/files/all_eas/"
  if not path.exists(src_folder):
    mkdir(src_folder)
    raise Exception('No source EA files found in', src_folder)
  src_folder_filenames = [f for f in listdir(src_folder) if '.mq4' in f]
  if len(src_folder_filenames) == 0:
    raise Exception("No EA files found in source folder:", src_folder)
  
  if not path.exists(mt_files_account_ea_folder):
    mkdir(mt_files_account_ea_folder)
    print('  Created new EA folder for account', account_id)
  files = [f for f in listdir(mt_files_account_ea_folder) if '.mq4' in f]
  # Delete existing files
  for filename in files:
      remove(mt_files_account_ea_folder + filename)
  print('  Deleted existing EA files in', mt_files_account_ea_folder)

  for strategyId, size in pos_sizes.items():
    found_filenames = [f for f in src_folder_filenames if str(strategyId) in f]
    if len(found_filenames) == 0:
      raise Exception("Could not find demo file with strategyId", strategyId)
    filename = found_filenames[0]
    # Copy required strategy file from source to account directory
    copy2(src_folder + filename, mt_files_account_ea_folder)
    # Update the contents with the applied position sizes  
    with open(f"{mt_files_account_ea_folder}{filename}", 'r') as f:
      content = f.read()
    sections = content.split('mmLots = ')
    part2 = sections[1][sections[1].index(';'):]
    new_content = f"{sections[0]}mmLots = {size:.2f}{part2}"
    with open(f"{mt_files_account_ea_folder}{filename}", 'w') as f:
      f.write(new_content)
  
  # Build and create template files
  templates_folder = getenv('MT_INSTANCES_DIR') + get_mt_instance_dir_name(account_id) + '/MQL4/Files/EaTemplates/'
  create_mt_templates(mt_files_account_ea_folder, templates_folder)
