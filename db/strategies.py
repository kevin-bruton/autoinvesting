from datetime import datetime
from collections import namedtuple
from db.common import query_many, query_one, mutate_one, values_placeholder, datetime_fmt
from db.trades import get_trades_of_account

strategy_fields = 'magic, strategyName, symbols, timeframes, description, workflow'
Strategy = namedtuple('Strategy', strategy_fields, defaults=(None, None))

def get_strategies ():
  # sql = "SELECT strategyName, magic, symbols, timeframes, btStart, btEnd, btDeposit, btKpis, demoStart, demoKpis FROM Strategies"
  sql = """SELECT strategyName, magic, 
    symbols, timeframes, description, workflow,
    STRFTIME('%Y-%m-%d %H:%i:%S', decommissioned) as decommissioned
    FROM Strategies"""
  return query_many(sql)

def get_all_strategy_kpis ():
  sql = 'SELECT accountNumber, accountType, annualPctRet, maxDD, maxPctDD, annPctRetVsDdPct, winPct, profitFactor, numTrades ' \
    + 'FROM Accounts WHERE accountType = ? OR accountType = ?'
  kpis = query_many(sql, ('strategy_backtest', 'strategy_demo'))
  return [ {
    'runType': 'backtest' if kpi['accountType'] == 'strategy_backtest' else 'demo',
    'magic': int(kpi['accountNumber']),
    'annualPctRet': float(kpi['annualPctRet']) if kpi['annualPctRet'] != None else None,
    'maxDD': float(kpi['maxDD']) if kpi['maxDD'] != None else None,
    'maxPctDD': float(kpi['maxPctDD']) if kpi['maxPctDD'] != None else None,
    'annPctRetVsDdPct': float(kpi['annPctRetVsDdPct']) if kpi['annPctRetVsDdPct'] != None else None,
    'winPct': float(kpi['winPct']) if kpi['winPct'] != None else None,
    'profitFactor': float(kpi['profitFactor']) if kpi['profitFactor'] != None else None,
    'numTrades': float(kpi['numTrades']) if kpi['numTrades'] != None else None
  } for kpi in kpis if kpi['accountType'] == 'strategy_backtest' or kpi['accountType'] == 'strategy_demo']

def get_strategy_summaries ():
  strategies = []
  strats = get_strategies()
  kpis_list = get_all_strategy_kpis()
  #return { 'strategies': strategies, 'kpis_list': kpis_list }
  for strat in strats:
    strategy = { k:strat[k] for k in strat.keys() }
    for strategy_kpis in kpis_list:
      if strategy_kpis['magic'] == strategy['magic']:
        runType = strategy_kpis['runType']
        run = { kpi:kpi_val for kpi, kpi_val in strategy_kpis.items() if kpi != 'runType' }
        strategy[runType] = run
    strategies.append(strategy)
  return strategies

def get_strategy_detail (magic):
  sql = "SELECT strategyName, symbols, timeframes, workflow, description FROM Strategies WHERE magic = ?"
  strategy = query_one(sql, (magic,))
  sql = 'SELECT accountId, startDate, endDate, deposit, annualPctRet, maxDD, maxPctDD, annPctRetVsDdPct, winPct, profitFactor, numTrades FROM Accounts WHERE accountNumber = ? AND accountType = ?'
  backtest = query_one(sql, (magic, 'strategy_backtest'))
  sql = 'SELECT accountId, startDate, annualPctRet, maxDD, maxPctDD, annPctRetVsDdPct, winPct, profitFactor, numTrades FROM Accounts WHERE accountNumber = ? AND accountType = ?'
  demo = query_one(sql, (magic, 'strategy_demo'))
  btTrades = get_trades_of_account(backtest['accountId'])
  demoTrades = get_trades_of_account(demo['accountId'])
  btKpis = {
    'annualPctRet': backtest['annualPctRet'],
    'maxDD': backtest['maxDD'],
    'maxPctDD': backtest['maxPctDD'],
    'annPctRetVsDdPct': backtest['annPctRetVsDdPct'],
    'winPct': backtest['winPct'],
    'profitFactor': backtest['profitFactor'],
    'numTrades': backtest['numTrades']
  }
  demoKpis = {
    'annualPctRet': demo['annualPctRet'],
    'maxDD': demo['maxDD'],
    'maxPctDD': demo['maxPctDD'],
    'annPctRetVsDdPct': demo['annPctRetVsDdPct'],
    'winPct': demo['winPct'],
    'profitFactor': demo['profitFactor'],
    'numTrades': demo['numTrades']
  }
  strategy = {
    'strategyName': strategy['strategyName'],
    'magic': magic,
    'symbols': strategy['symbols'],
    'timeframes': strategy['timeframes'],
    'btStart': str(backtest['startDate']),
    'btEnd': str(backtest['endDate']),
    'btDeposit': backtest['deposit'],
    'btTrades': btTrades if btTrades else [],
    'btKpis': btKpis,
    'demoStart': str(demo['startDate']),
    'demoTrades': demoTrades if demoTrades else [],
    'demoKpis': demoKpis
  }
  return strategy

def save_strategy (strategy):
  print('save-strategy:', strategy)
  sql = f"INSERT INTO Strategies ({strategy_fields}) VALUES ({values_placeholder(strategy_fields)})"
  return mutate_one(sql, strategy)

def decommission_strategy (magic):
  todays_datetime = datetime.strftime(datetime.now(), datetime_fmt)
  sql = 'UPDATE Strategies SET decommissioned=? WHERE magic=?'
  return mutate_one(sql, (todays_datetime, magic))

def reactivate_strategy (magic):
  sql = 'UPDATE Strategies SET decommissioned=? WHERE magic=?'
  return mutate_one(sql, (None, magic))
  
def get_all_strategy_data ():
  """ Get all strategy data from old db structure """
  sql = "SELECT strategyName,magic,symbols,timeframes,btStart,btEnd,btDeposit,btTrades,btKpis,demoStart,demoTrades,demoKpis FROM Strategies"
  return query_many(sql)

