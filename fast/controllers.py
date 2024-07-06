from os import listdir, path, remove
from shutil import copy2
from db.strategy_runs import StrategyRun, get_strategyrun_id, save_strategyrun
from fast.random_name import get_random_name
from db.strategies import Strategy, save_strategy, \
  decommission_strategy as decom_strategy, reactivate_strategy as react_strategy
from db.trades import Trade, get_strategys_backtest_trades, get_strategys_combined_trades, get_strategys_demo_trades, save_trade
from db.accounts import Account, save_account
from fast.utils import get_bt_kpis, get_project_root_dir
from datetime import datetime
import pandas as pd
from fast.create_templates import create_templates

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

def calc_correlation_matrix (strategyIds, strategyRunType, timeframe):
  """
    magic = list of integers
    data_type = 'demo', 'backtest' or 'combined'
    timeframe has to be 'D', 'W' or 'M'
  """
  data = pd.DataFrame()
  for strategyId in strategyIds:
    if strategyRunType == 'backtest':
      trades = get_strategys_backtest_trades(strategyId)
    elif strategyRunType == 'demo':
      trades = get_strategys_demo_trades(strategyId)
    elif strategyRunType == 'combined':
      trades = get_strategys_combined_trades(strategyId)
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
  correlation_json = data.corr().to_json(orient='columns')
  return '{ "data": ' + correlation_json + '}'

def decommission_strategy (magic):
  decom_strategy(magic)

def reactivate_strategy (magic):
  react_strategy(magic)

def apply_position_sizing (account_id, pos_sizes):
  folder = f"{get_project_root_dir()}/files/eas_to_install_on_live_account/"
  src_folder = f"{get_project_root_dir()}/files/eas_to_install_on_demo_account/"
  files = [f for f in listdir(folder) if '.mq4' in f]
  # Delete existing files
  for filename in files:
      remove(folder + filename)

  demo_filenames = [f for f in listdir(src_folder) if '.mq4' in f]
  for strategyId, size in pos_sizes.items():
    found_filenames = [f for f in demo_filenames if str(strategyId) in f]
    if len(found_filenames) == 0:
      raise Exception("Could not find demo file with strategyId", strategyId)
    filename = found_filenames[0]
    # Copy needed strategy file from demo to live directory
    copy2(src_folder + filename, folder)
    # Update the contents with the applied position sizes  
    with open(f"{folder}{filename}", 'r') as f:
      content = f.read()
    sections = content.split('mmLots = ')
    part2 = sections[1][sections[1].index(';'):]
    new_content = f"{sections[0]}mmLots = {size:.2f}{part2}"
    with open(f"{folder}{filename}", 'w') as f:
      f.write(new_content)
  
  # Build and create template files
  create_templates(account_id)
