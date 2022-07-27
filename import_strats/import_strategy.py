import json
from import_strats.random_name import get_random_name
from back.db import save_strategy
from mt_connector.kpis import get_bt_kpis

def get_strategy_trades (filepath):
  trades = []
  sani_date = lambda d: d.replace('.', '-')
  file = open(filepath, "r")
  line_num = 0
  for line in file:
    line_num += 1
    if line_num == 1:
      continue
    cells = line.strip().replace('"', '').split(';')
    trade = {
      'symbol': cells[1],
      'direction': cells[2], 
      'openTime': sani_date(cells[3]),
      'openPrice': float(cells[4]) if cells[4] else 0,
      'size': float(cells[5]),
      'closeTime': sani_date(cells[6]),
      'closePrice': float(cells[7]) if cells[7] else 0,
      'profit': float(cells[8]) if cells[8] else 0,
      'balance': float(cells[9]) if cells[9] else 0,
      'closeType': cells[11],
      'comment': cells[15]
    }
    trades.append(trade)
  file.close()
  return trades

def import_strategy (filename, filepath):
  basename = filename.split('.')[0]
  filename_parts = basename.split('_')
  magic = filename_parts[2]
  trades = get_strategy_trades(filepath)
  btStart = trades[0]['openTime']
  btEnd = trades[-1]['closeTime']
  details = {
    'strategyName': get_random_name(),
    'magic': magic,
    'symbols': filename_parts[0],
    'timeframes': filename_parts[1],
    'btStart': btStart,
    'btEnd': btEnd,
    'btTrades': json.dumps(trades),
    'btDeposit': 10000,
    'btKpis': json.dumps(get_bt_kpis(btStart, btEnd, trades, deposit=10000)),
    'demoStart': magic[0:4] + '-' + magic[4:6] + '-' + magic[6:8],
    'demoTrades': '[]'
  }
  save_strategy(details)
