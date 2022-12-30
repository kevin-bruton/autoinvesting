from os import listdir
from random_name import get_random_name
from db import Strategy, save_strategy, Trade, save_trade, Account, save_backtest, save_demorun
from utils import get_bt_kpis
from datetime import datetime

date_fmt = '%Y-%m-%d'

def save_new_strategies (upload_folder):
  folder = f"files/{upload_folder}"
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
      save_demorun(demo_run)
      for trade in trades:
        save_trade(trade)
  return True