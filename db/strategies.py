from datetime import datetime
from collections import namedtuple
from db.common import query_many, query_one, mutate_one, values_placeholder, datetime_fmt
from db.trades import get_trades_of_account

strategy_fields = 'strategyId, friendlyName, type, description, workflow, decommissioned'
Strategy = namedtuple('Strategy', strategy_fields, defaults=(None, None, None, None))

def get_strategies ():
  # sql = "SELECT strategyName, magic, symbols, timeframes, btStart, btEnd, btDeposit, btKpis, demoStart, demoKpis FROM Strategies"
  sql = """SELECT strategyId, friendlyName, 
    type, description, workflow,
    STRFTIME('%Y-%m-%d %H:%i:%S', decommissioned) as decommissioned
    FROM Strategies"""
  return query_many(sql)

def save_strategy (strategy: Strategy) -> int:
  print('save-strategy:', strategy)
  sql = f"INSERT INTO Strategies ({strategy_fields}) VALUES ({values_placeholder(strategy_fields)})"
  return mutate_one(sql, strategy)

def decommission_strategy (strategyId: str) -> int:
  todays_datetime = datetime.strftime(datetime.now(), datetime_fmt)
  sql = 'UPDATE Strategies SET decommissioned=? WHERE strategyId=?'
  return mutate_one(sql, (todays_datetime, strategyId))

def reactivate_strategy (strategyId):
  sql = 'UPDATE Strategies SET decommissioned=? WHERE strategyId=?'
  return mutate_one(sql, (None, strategyId))
  
def get_all_strategy_data ():
  """ Get all strategy data from old db structure """
  sql = "SELECT strategyId,friendlyName,type,description,workflow,decommissioned FROM Strategies"
  return query_many(sql)

