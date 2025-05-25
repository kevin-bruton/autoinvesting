import random
from db.trades import get_strategys_backtest_trades, get_strategys_combined_trades, get_strategys_live_trades
from fast.utils import normalize_position_sizes


def run_monte_carlo (balance, position_size, strategy_id, run_type, account_id, pct_trades, pct_confidence, num_simulations):
  print(f'run_monte_carlo. Balance: {balance}; PosSize: {position_size}; StratId: {strategy_id}; Type: {run_type}; AccId: {account_id}; %Trades: {pct_trades}; %Confid: {pct_confidence}; NumSims: {num_simulations}')
  if run_type == 'live':
    trades = get_strategys_live_trades(strategy_id, account_id)
  elif run_type == 'backtest':
      trades = get_strategys_backtest_trades(strategy_id)
  else:
    trades = get_strategys_combined_trades(strategy_id, account_id)
  
  trades = normalize_position_sizes(trades, position_size)
  simulations = []
  for i in range(num_simulations):
    # print('running simulation: ', i)
    # run simulation
    shuffled = shuffle_list(trades)
    skipped = skip_elements(shuffled, pct_trades)
    metrics = get_strategy_metrics(balance, position_size, skipped)
    simulations.append(metrics)
  
  mc_metrics = get_mc_metrics(simulations, pct_confidence)
  return mc_metrics

def shuffle_list (lst):
  # shuffle the list
  cpy = lst.copy()
  for cur_position in range(len(lst)):
    new_position = random.randint(0, len(lst) - 1)
    orig_open_time = cpy[cur_position]['openTime']
    new_position_open_time = cpy[new_position]['openTime']
    orig_close_time = cpy[cur_position]['closeTime']
    new_position_close_time = cpy[new_position]['closeTime']
    tmp = cpy[cur_position]
    cpy[cur_position] = cpy[new_position]
    cpy[cur_position]['openTime'] = new_position_open_time
    cpy[cur_position]['closeTime'] = new_position_close_time
    cpy[new_position] = tmp
    cpy[new_position]['openTime'] = orig_open_time
    cpy[new_position]['closeTime'] = orig_close_time
  return cpy

def skip_elements (lst, pct_to_skip):
  # skip elements
  cpy = lst.copy()
  num_to_skip = int(len(cpy) * pct_to_skip/100)
  while num_to_skip > 0 and cpy:
    cpy.pop(random.randint(0, len(cpy) - 1))
    num_to_skip -= 1
  return cpy

from datetime import datetime, timedelta
import math

def date_to_string(date):
    return date.strftime('%Y-%m-%d')

def dec2(value):
    return round(value, 2)

def difference_in_days(start_date, end_date):
    return (end_date - start_date).days

def get_ulcer_number(balances, trade_close_times):
    day_min_balances = {}
    for i in range(len(balances)):
        cur_trade_date = trade_close_times[i]
        if cur_trade_date in day_min_balances:
            if balances[i] < day_min_balances[cur_trade_date]:
                day_min_balances[cur_trade_date] = balances[i]
        else:
            day_min_balances[cur_trade_date] = balances[i]

    daily_drawdowns = {}
    last_high_balance = balances[0]
    cur_dd = 0
    for date in day_min_balances:
        cur_balance = day_min_balances[date]
        if cur_balance < last_high_balance:
            cur_dd = last_high_balance - cur_balance
        else:
            last_high_balance = cur_balance
            cur_dd = 0
        daily_drawdowns[date] = cur_dd

    sum_of_squared_drawdowns = sum(math.pow(dd, 2) for dd in daily_drawdowns.values())
    ulcer_number = math.sqrt(sum_of_squared_drawdowns / len(daily_drawdowns)) / balances[0] * 100
    return dec2(ulcer_number)

def get_strategy_metrics(account_balance, size, trades):
    if len(trades) == 0:
        return {
            'netProfit': 0,
            'annualPctRet': 0,
            'maxDD': 0,
            'maxPctDD': 0,
            'annPctRetVsDdPct': 0,
            'winPct': 0,
            'profitFactor': 0,
            'numTrades': 0,
            'profits': [],
            'stagnation': 0,
            'ulcerNumber': 0
        }
    account_balance = float(account_balance)
    
    size_multiplier = size / trades[0]['size']
    if size_multiplier != 1:
        trades = [{**t, 'profit': t['profit'] * size_multiplier} for t in trades]
    
    profits = [t['profit'] for t in trades]
    start_date = trades[0]['openTime'] - timedelta(days=1)
    end_date = trades[-1]['closeTime'] + timedelta(days=1)

    balances = [account_balance]
    trade_close_times = [start_date.strftime('%Y-%m-%d')]
    for trade in trades:
        balances.append(balances[-1] + trade['profit'])
        trade_close_times.append(trade['closeTime'])

    ulcer_number = get_ulcer_number(balances, trade_close_times)
    net_profit = dec2(balances[-1] - account_balance)
    total_pct_ret = dec2((balances[-1] - account_balance) / account_balance * 100)
    gross_profit = sum(p for p in profits if p > 0)
    gross_loss = sum(-p for p in profits if p < 0)
    profit_factor = dec2(gross_profit / gross_loss)
    num_backtest_days = difference_in_days(start_date, end_date)
    annual_pct_ret = dec2(total_pct_ret * (365 / num_backtest_days)) if num_backtest_days > 0 else 0

    last_high_balance = account_balance
    cur_dd = 0
    max_dd = 0
    last_high_time = trades[0]['closeTime']
    cur_stagnation = 0
    max_stagnation = 0
    for i in range(len(balances)):
        cur_balance = balances[i]
        cur_time = trades[i - 1]['closeTime'] if i > 0 else trades[0]['closeTime']
        if cur_balance < last_high_balance:
            cur_dd = last_high_balance - cur_balance
            cur_stagnation = difference_in_days(last_high_time, cur_time)
        elif cur_balance > last_high_balance:
            last_high_balance = cur_balance
            cur_dd = 0
            last_high_time = cur_time
            cur_stagnation = 0
        if cur_dd > max_dd:
            max_dd = cur_dd
        if cur_stagnation > max_stagnation:
            max_stagnation = cur_stagnation

    max_pct_dd = dec2(max_dd / account_balance * 100)
    ann_pct_ret_vs_dd_pct = dec2(annual_pct_ret / max_pct_dd)
    num_wins = sum(1 for p in profits if p > 0)
    win_pct = dec2(num_wins / len(profits) * 100)
    num_trades = len(trades)
    stagnation = max_stagnation

    return {
        'netProfit': net_profit,
        'annualPctRet': annual_pct_ret,
        'maxDD': max_dd,
        'maxPctDD': max_pct_dd,
        'annPctRetVsDdPct': ann_pct_ret_vs_dd_pct,
        'winPct': win_pct,
        'profitFactor': profit_factor,
        'numTrades': num_trades,
        'profits': profits,
        'stagnation': stagnation,
        'ulcerNumber': ulcer_number
    }

def get_mc_metrics(simulations, pct_confidence):
    annual_pct_ret = get_confidence_value(simulations, pct_confidence, 'annualPctRet')
    max_pct_dd = get_confidence_value(simulations, pct_confidence, 'maxPctDD')
    profit_factor = get_confidence_value(simulations, pct_confidence, 'profitFactor')
    stagnation = get_confidence_value(simulations, pct_confidence, 'stagnation')
    ulcer_number = get_confidence_value(simulations, pct_confidence, 'ulcerNumber')
    return {
        'maxPctDD': max_pct_dd,
        'profitFactor': profit_factor,
        'annualPctRet': annual_pct_ret,
        'stagnation': stagnation,
        'ulcerNumber': ulcer_number
    }

def get_confidence_value(simulations, percentile, metric_name):
    sort_order = {
        'annualPctRet': lambda x: sorted(x),
        'maxPctDD': lambda x: sorted(x),
        'profitFactor': lambda x: sorted(x),
        'stagnation': lambda x: sorted(x, reverse=True),
        'ulcerNumber': lambda x: sorted(x, reverse=True)
    }[metric_name]
    
    simulated_metrics = sort_order([sim[metric_name] for sim in simulations])
    cutoff_idx = percentile / 100 * len(simulations)
    lower_idx = int(cutoff_idx // 1)
    higher_idx = int(cutoff_idx // 1) + 1
    if higher_idx >= len(simulated_metrics):
        higher_idx = len(simulated_metrics) - 1
    lower_idx_value = simulated_metrics[lower_idx]
    higher_idx_value = simulated_metrics[higher_idx >= len(simulated_metrics) - 1] if higher_idx >= len(simulated_metrics) else simulated_metrics[higher_idx]
    return lower_idx_value + (higher_idx_value - lower_idx_value) * (cutoff_idx % 1)
