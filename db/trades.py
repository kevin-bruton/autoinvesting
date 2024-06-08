from collections import namedtuple
from db.common import mutate_many, mutate_one, query_many, query_one, datetime_fmt, values_placeholder

trade_fields = 'orderId, strategyRunId, symbol, orderType, openTime, closeTime, openPrice, closePrice, size, profit, balance, closeType, comment, sl, tp, swap, commission'
Trade = namedtuple('Trade', trade_fields, defaults=(None, None, None, None, None, None))

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
  '''
  return query_many(sql, (strategyId,))

def get_strategys_backtest_trades (magic):
  accountId = str(magic) + '_B'
  sql = 'SELECT orderId, accountId, symbol, orderType, openTime, closeTime, openPrice, closePrice, size, profit, closeType, comment ' \
    + 'FROM Trades WHERE accountId = ?'
  return query_many(sql, (accountId,))

def get_strategys_combined_trades (magic):
  backtest_trades = get_strategys_backtest_trades(magic)
  demo_trades = get_strategys_demo_trades(magic)
  return backtest_trades.extend(demo_trades)

def save_trade (trade: Trade):
  sql = f"INSERT INTO Trades ({trade_fields}) VALUES ({values_placeholder(trade_fields)})"
  return mutate_one(sql, trade)

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
