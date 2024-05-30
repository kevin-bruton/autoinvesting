import db1 as db1
import db

db1.init_db()
db.init_db()
""" 
users = db1.get_users()
for u in users:
    db2.save_user((
        u['accountType'],
        u['username'],
        u['passwd'],
        u['email'],
        u['firstName'],
        u['lastName'],
        u['city'],
        u['country']
    ))
 """
""" 
accounts = db1.get_accounts()
for account in accounts:
    if account['accountType'] == 'strategy_demo':
        db2.save_account(db2.Account(
            accountId='2089058421',
            accountType='paper',
            broker='Darwinex',
            platform='MetaTrader',
            username='kev7777'
        ))
 """
""" 
strategies = db1.get_strategies()
for strategy in strategies:
    db2.save_strategy(db2.Strategy(
        strategyId=str(strategy['magic']),
        friendlyName=strategy['strategyName']
    ))
 """
""" 
strategy_runs = db1.get_strategy_info()
for strat_run in strategy_runs:
    #print(dict(strat_run))
    db2.save_strategyrun(db2.StrategyRun(
        strategyId=str(strat_run['magic']),
        accountId='2089058421',
        symbol=strat_run['symbols'],
        timeframes=strat_run['timeframes'],
        startDate=strat_run['startDate'],
        type='paper'
    ))

strategy_runs = db1.get_strategy_info()
for strat_run in strategy_runs:
    #print(dict(strat_run))
    db2.save_strategyrun(db2.StrategyRun(
        strategyId=str(strat_run['magic']),
        symbol=strat_run['symbols'],
        timeframes=strat_run['timeframes'],
        startDate=strat_run['startDate'],
        endDate=strat_run['endDate'],
        type='backtest'
    ))
 """
"""
trades = db1.get_trades()
for trade in trades:
    #print(dict(trade))
    strategyId = str(trade['magic'])
    if strategyId == '0':
        continue
    runType = 'backtest' if trade['accountId'][-1:] == 'B' else 'paper'
    #print('strategyId:', strategyId, 'runType:', runType)
    strategyRunId = db2.get_trade_strategyrun_id(strategyId, runType)
    #print('strategyRunId:', strategyRunId)
    if not strategyRunId:
        print(dict(trade))
        print('strategyRunId:', strategyRunId, 'strategyId:', strategyId, 'runType:', runType)
    db2.save_trade(db2.Trade(
        orderId=trade['orderId'],
        strategyRunId=strategyRunId,
        symbol=trade['symbol'],
        orderType=trade['orderType'],
        openTime=trade['openTime'],
        closeTime=trade['closeTime'],
        openPrice=trade['openPrice'],
        closePrice=trade['closePrice'],
        size=trade['size'],
        profit=trade['profit'],
        balance=trade['balance'],
        closeType=trade['closeType'],
        comment=trade['comment'],
        sl=trade['sl'],
        tp=trade['tp'],
        swap=trade['swap'],
        commission=trade['commission']
    ))
"""


orders = db1.get_orders()
for order in orders:
    #print(dict(trade))
    strategyId = str(order['magic'])
    if strategyId == '0':
        continue
    runType = 'backtest' if order['accountId'][-1:] == 'B' else 'paper'
    #print('strategyId:', strategyId, 'runType:', runType)
    strategyRunId = db.get_trade_strategyrun_id(strategyId, runType)
    #print('strategyRunId:', strategyRunId)
    if not strategyRunId:
        print(dict(order))
        print('strategyRunId:', strategyRunId, 'strategyId:', strategyId, 'runType:', runType)
    db.save_order(db.Order(
        orderId=order['orderId'],
        strategyRunId=strategyRunId,
        status=order['status'],
        symbol=order['symbol'],
        orderType=order['orderType'],
        openTime=order['openTime'],
        openPrice=order['openPrice'],
        size=order['size'],
        comment=order['comment'],
        sl=order['sl'],
        tp=order['tp']
    ))

