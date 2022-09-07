import json
from datetime import datetime, timedelta
from back import db
from mt_connector.kpis import get_bt_kpis, get_demo_kpis
from dotenv import load_dotenv

def save_backtest (magic, startDate, endDate, deposit, trades):
  runId = db.save_backtest(magic, startDate, endDate, deposit)
  if runId:
    trades = json.loads(trades)
    for t in trades:
      db.save_trade(runId, t['symbol'], t['direction'], t['openTime'], t['closeTime'], t['openPrice'], t['closePrice'], t['size'], t['profit'], t['closeType'], t['comment'])
    kpis = get_bt_kpis(datetime.strftime(startDate, '%Y-%m-%d %H:%M:%S'), datetime.strftime(endDate, '%Y-%m-%d %H:%M:%S'), trades, deposit)
    db.save_kpis(runId, kpis['annualPctRet'], kpis['maxDD'], kpis['maxPctDD'], kpis['annPctRetVsDdPct'], kpis['winPct'], kpis['profitFactor'], kpis['numTrades'])

def save_demorun (magic, trades):
  trades = json.loads(trades)
  if len(trades):
    trades = [t for t in trades if t['closeTime']]
    start_date = datetime.strptime(trades[0]['openTime'][:10], '%Y-%m-%d') - timedelta(days=1)
  else:
    start_date = datetime.now()
  runId = db.save_demorun(magic, start_date.strftime('%Y-%m-%d'))
  if runId:
    for t in trades:
      db.save_trade(runId, t['symbol'], t['direction'], t['openTime'], t['closeTime'], t['openPrice'], t['closePrice'], t['size'], t['profit'], t['closeType'], t['comment'])
    kpis = get_demo_kpis(start_date, trades, deposit=3000)
    print('kpis:', kpis)
    db.save_kpis(runId, kpis['annualPctRet'], kpis['maxDD'], kpis['maxPctDD'], kpis['annPctRetVsDdPct'], kpis['winPct'], kpis['profitFactor'], kpis['numTrades'])

def save_strategies (strategies):
  for s in strategies:
    print(s[1])
    save_backtest(s[1], s[4], s[5], s[6], s[7])
    save_demorun(s[1], s[10])

def migrate_db ():
  strategies = db.get_all_strategy_data()
  save_strategies(strategies)

if __name__ == '__main__':
  load_dotenv()
  db.init_connection_pool()
  migrate_db()