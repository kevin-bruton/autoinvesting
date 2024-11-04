from datetime import datetime
from collections import namedtuple
from db.common import query_many, query_one, mutate_one, values_placeholder, datetime_fmt

strategyrun_fields = 'strategyId, accountId, symbol, timeframes, type, startDate, endDate, strategyRunId'
StrategyRun = namedtuple('Strategy', strategyrun_fields, defaults=(None, None, None, None, None, None, None))

def get_strategy_runs ():
  # sql = "SELECT strategyName, magic, symbols, timeframes, btStart, btEnd, btDeposit, btKpis, demoStart, demoKpis FROM Strategies"
  sql = """SELECT strategyRunId, strategyId, accountId, Strategies.symbol, Strategies.timeframe,
    strftime('%Y-%m-%d %H:%i:%S', startDate) as startDate,
    strftime('%Y-%m-%d %H:%i:%S', endDate) as endDate,
    FROM StrategyRuns
    INNER JOIN Strategies ON Strategies.strategyId = StrategyRuns.strategyId"""
  return query_many(sql)

# This function is deprecated - Must use get_strategyrunid instead
def get_strategyrun_id (strategyId: str, runType: str) -> int:
  print('get_strategyrun_id is deprecated. Refactor to use get_strategyrunid instead')
  sql = "SELECT strategyRunId FROM StrategyRuns WHERE strategyId = ? AND type = ?"
  result = query_one(sql, (strategyId, runType))
  if result and 'strategyRunId' in result.keys():
    return result['strategyRunId']
  return None

def get_strategyrunid (strategy_id: str, account_id: str) -> int:
  sql = "SELECT strategyRunId FROM StrategyRuns WHERE strategyId = ? AND accountId = ?"
  result = query_one(sql, (strategy_id, account_id))
  if result and 'strategyRunId' in result.keys():
    return result['strategyRunId']
  return None

def get_strategyrunid_backtest (strategy_id: str) -> int:
  sql = "SELECT strategyRunId FROM StrategyRuns WHERE strategyId = ? AND accountId IS NULL"
  result = query_one(sql, (strategy_id,))
  if result and 'strategyRunId' in result.keys():
    return result['strategyRunId']
  return None

def create_strategyrun (strategyId: str, accountId: str) -> int:
  sql = "INSERT INTO StrategyRuns (strategyId, accountId) VALUES (?, ?)"
  result = mutate_one(sql, (strategyId, accountId))
  if result:
    return get_strategyrunid(strategyId, accountId)
  return None

def save_strategyrun (strategyrun: StrategyRun) -> int:
  sql = f"INSERT INTO StrategyRuns ({strategyrun_fields}) VALUES ({values_placeholder(strategyrun_fields)})"
  return mutate_one(sql, strategyrun)

def get_account_strategyruns (account_id: str) -> list[StrategyRun]:
  sql = '''
      SELECT strategyRunId, friendlyName, Strategies.strategyId, Strategies.symbol, Strategies.timeframe, startDate, startingBalance
      FROM StrategyRuns
      INNER JOIN Strategies ON Strategies.strategyId = StrategyRuns.strategyId
      WHERE Strategies.decommissioned is NULL AND accountId = ?
    '''
  return query_many(sql, (account_id,))
