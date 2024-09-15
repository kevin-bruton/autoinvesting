import quantstats as qs
from os import getenv, listdir, path, getcwd
from requests import post
from os.path import join
from datetime import datetime, timedelta
from decimal import Decimal

# stock = qs.utils.download_returns('FB')

def get_returns_series(balances):
  pass

def get_project_root_dir ():
  return path.abspath(path.dirname(path.abspath(__file__)) + '/..')

def get_upload_folders ():
  files = listdir(get_project_root_dir() + '/files')
  files = [f for f in files if not path.isfile('files/' + f)] #Filtering only the directories.
  return files

def normalize_position_sizes (row_trades, normalized_trade_size=1):
  """
  Normalize the position sizes of trades to 1 and adjust profit of each trade accordingly.
  """
  trades = []
  for t in row_trades:
    trade = dict(t)
    multiplier = normalized_trade_size / trade['size']
    trade['size'] = normalized_trade_size
    trade['profit'] = round(trade['profit'] * multiplier, 2)
    trades.append(trade)
  return trades


def get_bt_kpis (btStart, btEnd, trades, deposit=10000):
  time_str_format = '%Y-%m-%d %H:%M:%S'
  start = datetime.combine(datetime.strptime(btStart, time_str_format), datetime.min.time())
  end = datetime.combine(datetime.strptime(btEnd, time_str_format), datetime.min.time())
  return get_kpis(start, end, trades, deposit)

def get_demo_kpis (start, trades, deposit=1000):
  start = datetime.combine(start, datetime.min.time()) # datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
  end = datetime.now()
  return get_kpis(start, end, trades, deposit)

def get_max_dd (start_dt, trades, balances):
  last_high = balances[0]
  cur_dd = 0
  max_dd = 0
  cur_stag = 0
  stagnation = 0
  last_high_date = start_dt
  for idx, trade in enumerate(trades):
    balance = balances[idx - 1 if idx else 0]
    if balance < last_high:
      cur_dd = last_high - balance
      cur_stag = (trades[idx]['closeTime'] - last_high_date).days
    elif balance > last_high:
      last_high = balance
      cur_dd = 0
      last_high_date = trade[idx]['closeTime']
      cur_stag = 0
    if cur_dd > max_dd:
      max_dd = cur_dd
    if cur_stag > stagnation:
      stagnation = cur_stag
  return max_dd, stagnation

def get_performance_metrics (trades):
  if len(trades) < 3:
    return {
      'annualPctRet': 0,
      'maxDD': 0,
      'maxPctDD': 0,
      'annPctRetVsDdPct': 0,
      'winPct': 0,
      'profitFactor': 0,
      'numTrades': 0
    }
  
  dt_format = '%Y-%m-%d %H:%M:%S'
  start = datetime.combine(trades[0]['openTime'], datetime.min.time())
  end = datetime.combine(trades[-1]['closeTime'], datetime.min.time())
  capital = 10000
  dec2 = lambda num: round(num * 100) / 100
  
  # print(' ***** Profits ***** ')
  # print('        ', profit)
  """ balances = [deposit]
  profit = []
  for i in range(0, len(trades)):
    profit.append(trades[i]['profit'])
    balances.append(balances[i] + profit[i])
  """

  gross_profit = 0
  gross_loss = 0
  num_wins = 0
  last_high_balance = capital
  cur_dd = 0
  max_dd = 0
  cur_stag = 0
  stagnation = 0
  last_high_date = start
  for idx, trade in enumerate(trades):
    # Calculate balances
    if idx == 0:
      trade['balance'] = capital + trade['profit']
    else:
      trade['balance'] = trades[idx - 1]['balance'] + trade['profit']
    # Calculate Gross Profit and Loss
    if trade['profit'] > 0:
      gross_profit += Decimal(trade['profit'])
    else:
      gross_loss -= Decimal(trade['profit'])
    # Calculate Number of Wins
    if trade['profit'] > 0:
      num_wins += 1
    # Calculate Max Drawdown and Stagnation
    if trade['balance'] < last_high_balance:
      cur_dd = last_high_balance - trade['balance']
      cur_stag = (trade['closeTime'] - last_high_date).days
    elif trade['balance'] > last_high_balance:
      last_high_balance = trade['balance']
      cur_dd = 0
      last_high_date = trade['closeTime']
      cur_stag = 0
    if cur_dd > max_dd:
      max_dd = cur_dd
    if cur_stag > stagnation:
      stagnation = cur_stag

  total_pct_ret = dec2((trades[-1]['balance'] - capital) / capital * 100)
  profit_factor = dec2(gross_profit / abs(gross_loss if gross_loss else 1))
  num_days = int((end - start).total_seconds() / 60 / 60 / 24)
  annual_pct_ret = dec2(total_pct_ret * 365 / num_days) if num_days else 0
  #max_dd = dec2(get_max_dd(start, trades, balances))
  max_pct_dd = dec2(max_dd / capital * 100)
  annual_pct_ret_vs_dd_pct = dec2(annual_pct_ret / max_pct_dd if max_pct_dd else 1)
  win_pct = dec2(num_wins / len(trades) * 100)
  return_vs_dd = dec2((trades[-1]['balance'] - capital) / max_dd if max_dd else 0)
  # print('    START:', start, '; END:', end)
  # print('    BALANCE START / END:', balances[0], dec2(balances[-1]))
  # print('    GROSS PROFIT / LOSS:', dec2(gross_profit), dec2(gross_loss))
  # print('    PCT RET:', total_pct_ret)
  # print('    NUM DAYS:', num_days)
  metrics = {
    'netProfit': dec2(trades[-1]['balance'] - capital),
    'annualPctRet': annual_pct_ret,
    'maxDD': dec2(max_dd),
    'maxPctDD': max_pct_dd,
    'annPctRetVsDdPct': annual_pct_ret_vs_dd_pct,
    'retDd': return_vs_dd,
    'winPct': win_pct,
    'profitFactor': profit_factor,
    'stagnation': stagnation,
    'numTrades': len(trades)
  }
  # print('    ', kpis)
  return capital, start, end, metrics

def dec2 (num):
  return round(num * 100) / 100

def get_kpis (start, end, trades, deposit):
  if not len(trades):
    return {
      'annualPctRet': 0,
      'maxDD': 0,
      'maxPctDD': 0,
      'annPctRetVsDdPct': 0,
      'winPct': 0,
      'profitFactor': 0,
      'numTrades': 0
    }
  profit = [t['profit'] for t in trades]
  
  # print(' ***** Profits ***** ')
  # print('        ', profit)
  balances = [deposit]
  for i in range(1, len(profit)):
    balances.append(balances[i-1] + profit[i])

  total_pct_ret = dec2((balances[-1] - deposit) / deposit * 100)
  gross_profit = 0
  gross_loss = 0
  for p in profit:
    if p > 0:
      gross_profit += Decimal(p)
    elif p < 0:
      gross_loss -= Decimal(p)
  profit_factor = dec2(gross_profit / abs(gross_loss if gross_loss else 1))
  num_days = int((end - start).total_seconds() / 60 / 60 / 24)
  annual_pct_ret = dec2(total_pct_ret * 365 / num_days) if num_days else 0
  max_dd = dec2(get_max_dd(start, trades, balances))
  max_pct_dd = dec2(max_dd / deposit * 100)
  annual_pct_ret_vs_dd_pct = dec2(annual_pct_ret / max_pct_dd if max_pct_dd else 1)
  num_wins = 0
  for p in profit:
    if p > 0:
      num_wins += 1
  win_pct = dec2(num_wins / len(profit) * 100)
  # print('    START:', start, '; END:', end)
  # print('    BALANCE START / END:', balances[0], dec2(balances[-1]))
  # print('    GROSS PROFIT / LOSS:', dec2(gross_profit), dec2(gross_loss))
  # print('    PCT RET:', total_pct_ret)
  # print('    NUM DAYS:', num_days)
  kpis = {
    'annualPctRet': annual_pct_ret,
    'maxDD': max_dd,
    'maxPctDD': max_pct_dd,
    'annPctRetVsDdPct': annual_pct_ret_vs_dd_pct,
    'winPct': win_pct,
    'profitFactor': profit_factor,
    'numTrades': len(trades)
  }
  # print('    ', kpis)
  return kpis
