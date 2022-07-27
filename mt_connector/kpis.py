from datetime import datetime

def get_max_dd (balances):
  last_high = balances[0]
  cur_dd = 0
  max_dd = 0
  for balance in balances:
    if balance < last_high:
      cur_dd = last_high - balance
    elif balance > last_high:
      last_high = balance
      cur_dd = 0
    if cur_dd > max_dd:
      max_dd = cur_dd
  return max_dd

def get_bt_kpis (btStart, btEnd, trades, deposit=10000):
  time_str_format = '%Y-%m-%d %H:%M:%S'
  start = datetime.combine(datetime.strptime(btStart, time_str_format), datetime.min.time())
  end = datetime.strptime(btEnd, time_str_format)
  return get_kpis(start, end, trades, deposit)

def get_demo_kpis (start, trades, deposit=1000):
  start = datetime.combine(start, datetime.min.time()) # datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
  end = datetime.now()
  return get_kpis(start, end, trades, deposit)

def get_kpis (start, end, trades, deposit):
  if not len(trades):
    return {
      'annualPctRet': 0,
      'maxDD': 0,
      'maxPctDD': 0,
      'annPctRetVsDdPct': 0,
      'winPct': 0,
      'profitFactor': 0
    }
  dec2 = lambda num: round(num * 100) / 100
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
      gross_profit += p
    elif p < 0:
      gross_loss -= p
  profit_factor = dec2(gross_profit / abs(gross_loss))
  num_days_on_demo = (end - start).total_seconds() / 60 / 60 / 24
  annual_pct_ret = dec2(total_pct_ret * 365 / num_days_on_demo)
  max_dd = get_max_dd(balances)
  max_pct_dd = dec2(max_dd / deposit * 100)
  annual_pct_ret_vs_dd_pct = dec2(annual_pct_ret / max_pct_dd)
  num_wins = 0
  for p in profit:
    if p > 0:
      num_wins += 1
  win_pct = dec2(num_wins / len(profit) * 100)
  print('START:', start, '; END:', end)
  print('BALANCE START / END:', balances[0], balances[-1])
  print('GROSS PROFIT / LOSS:', gross_profit, gross_loss)
  print('PCT RET:', total_pct_ret)
  print('NUM DAYS ON DEMO:', num_days_on_demo)
  return {
    'annualPctRet': annual_pct_ret,
    'maxDD': max_dd,
    'maxPctDD': max_pct_dd,
    'annPctRetVsDdPct': annual_pct_ret_vs_dd_pct,
    'winPct': win_pct,
    'profitFactor': profit_factor
  }



