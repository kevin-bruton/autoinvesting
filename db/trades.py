from datetime import datetime, timedelta
from collections import namedtuple
from db.common import mutate_many, mutate_one, query_many, query_one, datetime_fmt, values_placeholder
from db.strategy_runs import create_strategyrun, get_strategyrunid_backtest
from fast.utils import normalize_position_sizes

trade_fields = 'orderId, symbol, orderType, openTime, closeTime, openPrice, closePrice, size, profit, balance, strategyRunId, closeType, comment, sl, tp, swap, commission'
Trade = namedtuple('Trade', trade_fields, defaults=(None, None, None, None, None, None, None))

def get_trade_strategyrun_id(strategyId, runType):
  sql = "SELECT strategyRunId FROM strategyRuns WHERE strategyId = ? AND type = ?"
  result = query_one(sql, (strategyId, runType))
  if result and 'strategyRunId' in result.keys():
    return result['strategyRunId']
  return None

def get_trades ():
  sql = f'SELECT {trade_fields} FROM Trades'
  trades = query_many(sql)
  return [{**trade, **{
      'openTime': trade['openTime'].strftime('%Y-%m-%d %H:%M:%S'),
      'closeTime': trade['closeTime'].strftime('%Y-%m-%d %H:%M:%S'),
      'size': float(trade['size']),
      'profit': float(trade['profit'])
    }} for trade in trades]

def get_trades_of_account (account_id):
  sql = 'SELECT symbol, orderType, openTime, closeTime, openPrice, closePrice, size, profit, closeType, comment FROM Trades WHERE accountId = ? ORDER BY closeTime'
  trades = query_many(sql, (account_id,))
  return [{**trade, **{
      'openTime': trade['openTime'],
      'closeTime': trade['closeTime'],
      'size': float(trade['size']),
      'profit': float(trade['profit'])
    }} for trade in trades]

def get_next_free_order_id ():
  trades = get_trades()
  order_ids = [trade['orderId'] for trade in trades]
  for test_order_id in range(len(order_ids) + 1):
    if test_order_id not in order_ids:
      return test_order_id

def get_account_trades (account_id):
  sql = 'SELECT * FROM Trades WHERE accountId = ?'
  trades = query_many(sql, (account_id,))
  return [{**t, **{
    'openTime': t['openTime'].strftime(datetime_fmt),
    'closeTime': t['closeTime'].strftime(datetime_fmt),
    'openPrice': float(t['openPrice']),
    'closePrice': float(t['closePrice']),
    'size': float(t['size']),
    'profit': float(t['profit']),
    'balance': float(t['balance']) if t['balance'] else 0,
    'sl': float(t['sl']) if t['sl'] else None,
    'tp': float(t['tp']) if t['tp'] else None,
    'swap': float(t['swap']) if t['swap'] else 0,
    'commission': float(t['commission']) if t['commission'] else 0
    }} for t in trades]

def get_strategys_demo_trades (strategyId):
  sql = '''
    SELECT orderId, accountId, orderType, openTime, closeTime, openPrice, closePrice, size, profit, closeType, comment
    FROM Trades
    INNER JOIN StrategyRuns ON Trades.strategyRunId = StrategyRuns.strategyRunId
    WHERE StrategyRuns.strategyId = ? AND StrategyRuns.type = 'paper'
    ORDER BY closeTime
  '''
  return query_many(sql, (strategyId,))

def get_strategys_live_trades (strategyId, accountId, from_date=None):
  if from_date:
    sql = '''
      SELECT orderId, accountId, orderType, openTime, closeTime, openPrice, closePrice, size, profit, closeType, comment
      FROM Trades
      INNER JOIN StrategyRuns ON Trades.strategyRunId = StrategyRuns.strategyRunId
      WHERE StrategyRuns.strategyId = ? AND StrategyRuns.accountId = ? AND closeTime >= ?
      ORDER BY closeTime
    '''
    trades = query_many(sql, (strategyId, accountId, from_date,))
  else:
    sql = '''
      SELECT orderId, accountId, orderType, openTime, closeTime, openPrice, closePrice, size, profit, closeType, comment
      FROM Trades
      INNER JOIN StrategyRuns ON Trades.strategyRunId = StrategyRuns.strategyRunId
      WHERE StrategyRuns.strategyId = ? AND StrategyRuns.accountId = ?
      ORDER BY closeTime
    '''
    trades = query_many(sql, (strategyId, accountId,))
  return [
      {**dict(trade), 
       'openTime': datetime.strptime(trade['openTime'][:19], '%Y-%m-%d %H:%M:%S'), 
       'closeTime': datetime.strptime(trade['closeTime'][:19], '%Y-%m-%d %H:%M:%S')}
      for trade in trades
    ]

def get_strategys_oos_start (strategyId):
  sql = '''
    SELECT oosStart
    FROM Strategies
    WHERE strategyId = ?
  '''
  result = query_one(sql, (strategyId,))
  return result['oosStart'] if result and 'oosStart' in result.keys() else None

def get_strategys_backtest_trades (strategyId, up_until_date=None, from_date=None):
  if up_until_date:
    sql = '''
      SELECT orderId, orderType, openTime, closeTime, openPrice, closePrice, size, profit, closeType, comment
      FROM Trades
      INNER JOIN StrategyRuns ON Trades.strategyRunId = StrategyRuns.strategyRunId
      WHERE StrategyRuns.strategyId = ? AND StrategyRuns.accountId = 'sqx_bkt_original' AND closeTime < ?
      ORDER BY closeTime
    '''
    trades = query_many(sql, (strategyId, up_until_date,))
  elif from_date:
    sql = '''
      SELECT orderId, orderType, openTime, closeTime, openPrice, closePrice, size, profit, closeType, comment
      FROM Trades
      INNER JOIN StrategyRuns ON Trades.strategyRunId = StrategyRuns.strategyRunId
      WHERE StrategyRuns.strategyId = ? AND StrategyRuns.accountId IS NULL AND closeTime >= ?
      ORDER BY closeTime
    '''
    trades = query_many(sql, (strategyId, from_date,))
  else:
    sql = '''
        SELECT orderId, orderType, openTime, closeTime, openPrice, closePrice, size, profit, closeType, comment, Trades.strategyRunId
        FROM Trades
        INNER JOIN StrategyRuns ON Trades.strategyRunId = StrategyRuns.strategyRunId
        WHERE StrategyRuns.strategyId = ? AND StrategyRuns.accountId IS NULL
        ORDER BY closeTime
      '''
    trades = query_many(sql, (strategyId,))
  return [
    {**dict(trade), 
      'openTime': datetime.strptime(trade['openTime'], '%Y-%m-%d %H:%M:%S'), 
      'closeTime': datetime.strptime(trade['closeTime'], '%Y-%m-%d %H:%M:%S')}
    for trade in trades
  ]

def get_strategys_combined_trades (strategyId, accountId):
  live_trades = get_strategys_live_trades(strategyId, accountId)
  if len(live_trades) == 0:
    return get_strategys_backtest_trades(strategyId)
  live_start = (live_trades[0]['closeTime'] - timedelta(days=1)) if live_trades else datetime.now().strftime('%Y-%m-%d')
  backtest_trades = get_strategys_backtest_trades(strategyId, up_until_date=live_start)
  backtest_trades = normalize_position_sizes(backtest_trades, live_trades[0]['size'])
  backtest_trades.extend(live_trades)
  return backtest_trades

def save_trade (trade: Trade):
  sql = f"INSERT INTO Trades ({trade_fields}) VALUES ({values_placeholder(trade_fields)})"
  return mutate_one(sql, trade)

# Function to check if a trade already exists in the database
def trade_exists(order_id):
  sql = 'SELECT 1 FROM trades WHERE orderId = ?'
  return query_one(sql, (order_id,)) is not None

def save_backtest_trades(strategy_id, headers: list[str], trades: list[list[str|int|float]]):
  #trade_fields = 'orderId, symbol, orderType, openTime, closeTime, openPrice, closePrice, size, profit, balance, strategyRunId, closeType, comment, sl, tp, swap, commission'
  strategy_run_id = get_strategyrunid_backtest(strategy_id)
  if not strategy_run_id:
    create_strategyrun(strategy_id, None)
  else:
    # delete existing trades
    sql = 'DELETE FROM Trades WHERE strategyRunId = ?'
    num_deleted = mutate_one(sql, (strategy_run_id,))
    print('Number of old backtest trades deleted:', num_deleted)
  for trade in trades:
    trade[10] = strategy_run_id
  sql = f"INSERT INTO Trades ({trade_fields}) VALUES ({values_placeholder(trade_fields)})"
  return mutate_many(sql, trades)

def update_trade_magic (orderId, magic):
  sql = 'UPDATE Trades SET magic = ? WHERE orderId = ?'
  return mutate_one(sql, (magic, orderId,))

def get_strategyrun_trades (strategyrun_id):
  sql = '''
      SELECT orderId, strategyRunId, symbol, orderType, openTime, closeTime, openPrice, closePrice, size, profit, balanace, closeType, comment, sl, tp, swap, commission
      FROM Trades
      WHERE strategyRunId = ?
    '''
  return query_many(sql, (strategyrun_id,))
