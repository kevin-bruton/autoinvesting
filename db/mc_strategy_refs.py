from datetime import datetime
from collections import namedtuple
from db.common import query_many, query_one, mutate_one, values_placeholder, datetime_fmt

def register_mc_strategy_ref (strategyRef,chartSymbol,chartRootSymbol,chartExchange,dataProvider,brokerSymbol,brokerRootSymbol,brokerExchange,broker,brokerProfile,accountId,workspace,strategyName,regDatetime):
  sql = '''INSERT INTO McStrategyRefs (strategyRef,chartSymbol,chartRootSymbol,chartExchange,dataProvider,brokerSymbol,brokerRootSymbol,brokerExchange,broker,brokerProfile,accountId,workspace,strategyName,regDatetime)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
          ON CONFLICT(strategyRef)
          DO UPDATE SET chartSymbol=?,chartRootSymbol=?,chartExchange=?,dataProvider=?,brokerSymbol=?,brokerRootSymbol=?,brokerExchange=?,broker=?,brokerProfile=?,accountId=?,workspace=?,strategyName=?,regDatetime=?'''
  return mutate_one(sql, (strategyRef,chartSymbol,chartRootSymbol,chartExchange,dataProvider,brokerSymbol,brokerRootSymbol,brokerExchange,broker,brokerProfile,accountId,workspace,strategyName,regDatetime,chartSymbol,chartRootSymbol,chartExchange,dataProvider,brokerSymbol,brokerRootSymbol,brokerExchange,broker,brokerProfile,accountId,workspace,strategyName,regDatetime))

def get_mc_strategy_refs ():
  sql = '''SELECT strategyRef,chartSymbol,chartRootSymbol,chartExchange,dataProvider,brokerSymbol,brokerRootSymbol,brokerExchange,broker,brokerProfile,accountId,workspace,strategyName,regDatetime
           FROM McStrategyRefs'''
  return query_many(sql)