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

def save_strategyrun (strategyrun: StrategyRun) -> int:
  sql = f"INSERT INTO StrategyRuns ({strategyrun_fields}) VALUES ({values_placeholder(strategyrun_fields)})"
  return mutate_one(sql, strategyrun)
