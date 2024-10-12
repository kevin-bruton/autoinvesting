from datetime import datetime
from collections import namedtuple
from db.common import query_many, query_one, mutate_one, values_placeholder, datetime_fmt
from db.trades import get_trades_of_account

strategyrun_fields = 'strategyId, accountId, symbol, timeframes, type, startDate, endDate, strategyRunId'
StrategyRun = namedtuple('Strategy', strategyrun_fields, defaults=(None, None, None, None, None, None, None))

def get_strategy_runs ():
  # sql = "SELECT strategyName, magic, symbols, timeframes, btStart, btEnd, btDeposit, btKpis, demoStart, demoKpis FROM Strategies"
  sql = """SELECT strategyRunId, strategyId, accountId, type, symbol, timeframe,
    strftime('%Y-%m-%d %H:%i:%S', startDate) as startDate,
    strftime('%Y-%m-%d %H:%i:%S', endDate) as endDate,
    FROM StrategyRuns"""
  return query_many(sql)

def get_strategyrun_id (strategyId: str, runType: str) -> int:
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
  return get_strategyrun_id(strategy_id, 'backtest')

def save_strategyrun (strategyrun: StrategyRun) -> int:
  sql = f"INSERT INTO StrategyRuns ({strategyrun_fields}) VALUES ({values_placeholder(strategyrun_fields)})"
  return mutate_one(sql, strategyrun)

def get_account_strategyruns (account_id: str) -> list[StrategyRun]:
  sql = '''
      SELECT strategyRunId, friendlyName, Strategies.strategyId, StrategyRuns.type, symbol, timeframes, startDate, startingBalance
      FROM StrategyRuns
      INNER JOIN Strategies ON Strategies.strategyId = StrategyRuns.strategyId
      WHERE Strategies.decommissioned is NULL AND accountId = ?
    '''
  return query_many(sql, (account_id,))

def create_paper_strategyrun (strategyId: str) -> int:
  sql = "INSERT INTO StrategyRuns (strategyId, type) VALUES (?, 'paper')"
  return mutate_one(sql, (strategyId,))
