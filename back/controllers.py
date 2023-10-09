from os import listdir
from random_name import get_random_name
from db import Strategy, save_strategy, Trade, save_trade, \
  Account, save_backtest, save_account, \
  get_strategys_backtest_trades, get_strategys_demo_trades, get_strategys_combined_trades, \
  decommission_strategy as decom_strategy, reactivate_strategy as react_strategy
from utils import get_bt_kpis, get_project_root_dir
from datetime import datetime
import pandas as pd

date_fmt = '%Y-%m-%d'

def save_new_strategies (upload_folder):
  folder = f"{get_project_root_dir()}/files/{upload_folder}"
  files = listdir(folder)
  csv_files = [f for f in files if f[-3:] == 'csv']
  deposit = 1000
  for filename in csv_files:
    base_filename = filename[:-4]
    symbol, timeframe, magic = base_filename.split('_')
    name = get_random_name()
    strategy = Strategy(magic, name, symbol, timeframe)
    save_strategy(strategy)
    print('Saved strategy', name, base_filename)
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
          orderId=f"{l[0]}_{magic}_B",
          masterOrderId=None,
          accountId=f"{magic}_B",
          magic=magic,
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
      kpis = get_bt_kpis(start_date, end_date, trades, deposit)
      print(kpis)
      backtest = Account(
        accountId=f"{magic}_B",
        accountNumber=magic,
        accountType='strategy_backtest',
        username='master',
        subscriptionKey=None,
        annualPctRet=kpis['annualPctRet'],
        maxDD=kpis['maxDD'],
        maxPctDD=kpis['maxPctDD'],
        annPctRetVsDdPct=kpis['annPctRetVsDdPct'],
        winPct=kpis['winPct'],
        profitFactor=kpis['profitFactor'],
        numTrades=kpis['numTrades'],
        startDate=start_date,
        endDate=end_date,
        deposit=deposit,
      )
      save_backtest(backtest)
      demo_run = Account(
        accountId=f"{magic}_D",
        accountNumber=magic,
        accountType='strategy_demo',
        username='master',
        subscriptionKey=None,
        annualPctRet=None,
        maxDD=None,
        maxPctDD=None,
        annPctRetVsDdPct=None,
        winPct=None,
        profitFactor=None,
        numTrades=0,
        startDate=datetime.now().strftime(date_fmt),
        endDate=None,
        deposit=1000
      )
      save_account(demo_run)
      for trade in trades:
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

def calc_correlation_matrix (magics, data_type, timeframe):
  """
    magic = list of integers
    data_type = 'demo', 'backtest' or 'combined'
    timeframe has to be 'D', 'W' or 'M'
  """
  data = pd.DataFrame()
  for magic in magics:
    if data_type == 'backtest':
      trades = get_strategys_backtest_trades(magic)
    elif data_type == 'demo':
      trades = get_strategys_demo_trades(magic)
    elif data_type == 'combined':
      trades = get_strategys_combined_trades(magic)
    df = pd.DataFrame(trades)
    df = df[['closeTime', 'profit']]
    df = df.groupby(pd.Grouper(key='closeTime', freq=timeframe)).sum()
    df[magic] = df['profit'].cumsum().astype(float)
    # df['profit_'+str(magic)] = df['profit']
    df = df.drop(columns='profit')
    if data.empty:
      data = df
    else:
      data = pd.concat([data, df], axis=1, join='outer').fillna(0)
  return '{ "data": ' + data.corr().to_json(orient='columns') + '}'

def decommission_strategy (magic):
  decom_strategy(magic)

def reactivate_strategy (magic):
  react_strategy(magic)
