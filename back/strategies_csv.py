from db import save_strategy
from time import sleep

def save_strategies_csv (csv_content):
  print('GOING TO SAVE STRATEGIES CSV **********')
  print(csv_content)
  results = []
  lines = csv_content.split('\n')
  for idx in range(1, len(lines)):
    # sleep(1)
    line = lines[idx].strip()
    if not line:
      continue
    fields = line.split(';')
    details = {}
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
      save_strategy(details)
      results.append({ 'magic': details['magic'], 'error': None })
    except Exception as e:
      results.append({ 'magic': details['magic'], 'error': repr(e)})
  return {'results': results}
