from email.mime import base
import json
from datetime import datetime, timedelta

from dotenv import load_dotenv

from back import db
from back.utils import get_bt_kpis, get_demo_kpis


def save_backtest (magic, startDate, endDate, deposit, trades):
  trades = json.loads(trades)
  startDate = f'{startDate} 00:00:00'
  endDate = f'{endDate} 00:00:00'
  kpis = get_bt_kpis(startDate, endDate, trades, deposit)
  runId = str(magic) + '_B'
  backtest = db.StrategyRun(
    runId,
    magic,
    kpis['annualPctRet'],
    kpis['maxDD'],
    kpis['maxPctDD'],
    kpis['annPctRetVsDdPct'],
    kpis['winPct'],
    kpis['profitFactor'],
    kpis['numTrades'],
    startDate,
    endDate=endDate,
    deposit=deposit
  )
  success = db.save_backtest(backtest)
  if success:
    for i, t in enumerate(trades):
      orderId = f"{str(i)}_{runId}"
      trade = db.Trade(orderId, runId, t['symbol'], t['direction'], t['openTime'], t['closeTime'], t['openPrice'], t['closePrice'], t['size'], t['profit'], t['closeType'], t['comment'])
      db.save_trade(trade)

def save_demorun (magic, trades):
  base_deposit = 3000
  runId = str(magic) + '_D'
  trades = json.loads(trades)
  if len(trades):
    trades = [t for t in trades if t['closeTime']]
    start_date = datetime.strptime(trades[0]['openTime'][:10], '%Y-%m-%d') - timedelta(days=1)
  else:
    start_date = datetime.now()
  kpis = get_demo_kpis(start_date, trades, deposit=base_deposit)
  demorun = db.StrategyRun(runId, magic, kpis['annualPctRet'], kpis['maxDD'], kpis['maxPctDD'], kpis['annPctRetVsDdPct'], kpis['winPct'], kpis['profitFactor'], kpis['numTrades'], start_date.strftime('%Y-%m-%d'),deposit=base_deposit)
  success = db.save_demorun(demorun)
  if success:
    for t in trades:
      order_id = f"{t['orderId']}_{runId}"
      trade = db.Trade(order_id, runId, t['symbol'], t['direction'], t['openTime'], t['closeTime'], t['openPrice'], t['closePrice'], t['size'], t['profit'], t['closeType'], t['comment'], t['sl'], t['tp'], t['swap'], t['commission'])
      db.save_trade(trade)

def save_strategies (strategies):
  for s in strategies:
    if s['magic'] == 0: continue
    save_backtest(s['magic'], s['btStart'], s['btEnd'], s['btDeposit'], s['btTrades'])
    save_demorun(s['magic'], s['demoTrades'])
    print('Saved', s['strategyName'], s['magic'])

def migrate_db ():
  strategies = db.get_all_strategy_data()
  save_strategies(strategies)

if __name__ == '__main__':
  load_dotenv()
  db.init_connection_pool()
  migrate_db()