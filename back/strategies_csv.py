import json

from db import User, Strategy, Account, Trade, Position, Subscription
import db


def save_all_strategy_data (content):
  results = []
  data = json.loads(content)
  users = data['users']
  strategies = data['strategies']
  accounts = data['accounts']
  trades = data['trades']
  positions = data['positions']
  subscriptions = data['subscriptions']
  
  for u in users:
    user = User(u['accountType'], u['username'], u['passwd'], u['email'], u['firstName'], u['lastName'], u['city'], u['country'])
    try:
      res = db.save_user(user)
      results.append({ 'save_user': u['username'], 'success': True })
    except Exception as e:
      results.append({ 'save_user': u['username'], 'success': False, 'error': repr(e) })
  for s in strategies:
    strategy = Strategy(s['magic'], s['strategyName'], s['symbols'], s['timeframes'], s['description'], s['workflow'])
    try:
      res = db.save_strategy(strategy)
      results.append({ 'save_strategy': strategy.magic, 'success': True })
    except Exception as e:
      results.append({ 'save_strategy': strategy.magic, 'success': False, 'error': repr(e) })
  for a in accounts:
    account = Account(a['accountId'], a['accountNumber'], a['accountType'], a['username'], a['annualPctRet'], a['maxDD'], a['maxPctDD'], a['annPctRetVsDdPct'], a['winPct'], a['profitFactor'], a['numTrades'], a['startDate'], a['endDate'], a['deposit'])
    try:
      res = db.save_account(account)
      results.append({ 'save_account': account.accountId, 'success': True })
    except Exception as e:
      results.append({ 'save_account': account.accountId, 'success': False, 'error': repr(e) })
  for t in trades:
    trade = Trade(
      t['orderId'],
      t['masterOrderId'],
      t['accountId'],
      t['magic'],
      t['symbol'],
      t['orderType'],
      t['openTime'],
      t['closeTime'],
      t['openPrice'],
      t['closePrice'],
      t['size'],
      t['profit'],
      t['balance'],
      t['closeType'] if 'closeType' in t else None,
      t['comment'] if 'comment' in t else None,
      t['sl'] if 'sl' in t else None,
      t['tp'] if 'tp' in t else None,
      t['swap'] if 'swap' in t else None,
      t['commission'] if 'commission' in t else None
    )
    try:
      res = db.save_trade(trade)
      results.append({ 'save_trade': trade.orderId, 'success': True })
    except Exception as e:
      results.append({ 'save_trade': trade.orderId, 'success': False, 'error': repr(e) })
  for p in positions:
    position = Position(
      p['orderId'],
      p['masterOrderId'],
      p['accountId'],
      p['magic'],
      p['symbol'],
      p['orderType'],
      p['openTime'],
      p['openPrice'],
      p['size'],
      p['comment'] if 'comment' in t else None,
      p['sl'] if 'sl' in t else None,
      p['tp'] if 'tp' in t else None
    )
    try:
      res = db.save_position(position)
      results.append({ 'save_position': p['orderId'], 'success': True })
    except Exception as e:
      results.append({ 'save_position': p['orderId'], 'success': False, 'error': repr(e) })
  for sb in subscriptions:
    subscription = Subscription(sb['accountId'], sb['magic'])
    try:
      res = db.save_subscription(subscription)
      results.append({ 'save_subscription': f"{sb['accountId']}_{sb['magic']}", 'success': True })
    except Exception as e:
      results.append({ 'save_subscription': f"{sb['accountId']}_{sb['magic']}", 'success': False, 'error': repr(e) })
  return {'results': results}

def save_strategies_csv (csv_content):
  print('GOING TO SAVE STRATEGIES CSV **********')
  results = []
  lines = csv_content.split('\n')
  print('Num lines:', len(lines))
  for idx in range(1, len(lines)):
    # sleep(1)
    line = lines[idx].strip()
    if not line:
      continue
    fields = line.split(';')
    if idx == 1:
      print('  First line:', line)
      print('  Num fields:', len(fields))
    details = {}
    if len(fields) == 12:
      details['strategyName'] = fields[0] if fields[0] else None
      details['magic'] = fields[1] if fields[1] else None
      details['symbols'] = fields[2] if fields[2] else None
      details['timeframes'] = fields[3] if fields[3] else None
      details['btStart'] = fields[4] if fields[4] else None
      details['btEnd'] = fields[5] if fields[5] else None
      details['btDeposit'] = fields[6] if fields[6] else None
      details['btTrades'] = fields[7] if fields[7] else None
      details['btKpis'] = fields[8] if fields[8] else None
      details['demoStart'] = fields[9] if fields[9] else None
      details['demoTrades'] = fields[10] if fields[10] else None
      details['demoKpis'] = fields[11] if fields[11] else None
    else:
      details['strategyName'] = fields[0] if fields[0] else None
      details['magic'] = fields[1] if fields[1] else None
      details['symbols'] = fields[2] if fields[2] else None
      details['timeframes'] = fields[3] if fields[3] else None
      details['btStart'] = fields[4] if fields[4] else None
      details['btEnd'] = fields[5] if fields[5] else None
      details['btTrades'] = fields[6] if fields[6] else None
      details['demoStart'] = fields[7] if fields[7] else None
      details['demoTrades'] = fields[8] if fields[8] else None
    
    try:
      db.save_strategy(details)
      results.append({ 'magic': details['magic'], 'error': None })
    except Exception as e:
      results.append({ 'magic': details['magic'], 'error': repr(e)})
  return {'results': results}
