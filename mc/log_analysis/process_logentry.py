from copy import deepcopy
from datetime import datetime

from db.mc_raw_orders import RawOrder, register_mc_raw_order
from db.mc_strategy_refs import register_mc_strategy_ref
from fast.routers.send_sse import send_sse

strategies = []
orders = []

def _tsToStr(ts):
  return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S.%f')

def _logtimeToTs(str):
  return datetime.strptime(str, '%d.%m.%Y/%H:%M:%S.%f').timestamp()

def _getKeyValue(content, key):
  key_idx = content.find(key)
  if key_idx == -1:
    return ''
  value_idx = key_idx + len(key) + 1
  value_end_idx = content.find(';', value_idx)
  return content[value_idx:value_end_idx]

def _getSymbol(content):
  brSymbol = _getKeyValue(content, 'BrSymbol')
  cqgSplit = brSymbol.split('CQG')
  if len(cqgSplit) == 2:
    return cqgSplit[0]
  ibSplit = brSymbol.split('Interactive')
  if len(ibSplit) == 2:
    return ibSplit[0]
  return brSymbol

def _isStrategyIdentifier(content):
  return content.count('{"') == 2 and content.count('"') == 30

def _processStrategyIdentifier(logentry_ts, content):
  start_idx = content.index(';') + 1
  end_idx = content.index(';', start_idx + 1)
  data = [content[start_idx:end_idx]]
  for i in range(15):
    start_idx = content.index('"', end_idx) + 1
    end_idx = content.index('"', start_idx + 1)
    data.append(content[start_idx:end_idx])
    end_idx += 2
  register_mc_strategy_ref(
    strategyRef = data[0],
    chartSymbol = data[1],
    chartRootSymbol = data[2],
    chartExchange = data[4],
    dataProvider = data[5],
    brokerSymbol = data[6],
    brokerRootSymbol = data[7],
    brokerExchange = data[9],
    broker = data[10],
    brokerProfile = data[12],
    accountId = data[13],
    workspace = data[14],
    strategyName = data[15],
    regDatetime=logentry_ts
  )
  print("Strategy registered. strategyRef:", data[0], "strategyName:", data[15], "workspace:", data[14])
  send_sse('logprocessing', 'Strategy registered. strategyRef: ' + data[0] + ' strategyName: ' + data[15] + ' workspace: ' + data[14])
  """
  found_strategies = [s for s in strategies if s['strategyId'] == strategyId]
  if len(found_strategies) == 0:
    strategies.append({
      'strategyRef': strategyRef,
      'strategyName': strategyName,
      'workspace': workspace,
      'account': account,
      'brokerProfile': brokerProfile,
      'symbol': symbol,
      'symbolRoot': symbolRoot,
      'exchange': exchange,
      'currency': currency,
      'regDate': _tsToStr(logentry_ts)
      })
  """
  
def _isOrderEvent(content):
  columns = content.split(' ')
  return len(columns) > 0 \
    and 'PDS' in columns[0]

def _processOrderEvent(content):
  state = _getKeyValue(content, 'State')
  if state != 'Filled':
    #print('  Ignoring event. State:', state)
    return
  orderId = int(_getKeyValue(content, 'OrderID').split(',')[0])
  brokerId = int(_getKeyValue(content, 'BrIDStr'))
  strategyRef = int(_getKeyValue(content, 'ELTraderID'))
  action = _getKeyValue(content, 'Actn')
  category = _getKeyValue(content, 'Cat')
  generatedTs = _getKeyValue(content, 'Gen')
  finalTs = _getKeyValue(content, 'Final')
  initialPrice = float(_getKeyValue(content, 'Price'))
  fillPrice = float(_getKeyValue(content, 'FillPrice'))
  qty = int(_getKeyValue(content, 'Qty'))
  fillQty = int(_getKeyValue(content, 'FillQty'))
  brokerProfile = _getKeyValue(content, 'Broker')
  account = _getKeyValue(content, 'Account')
  symbol = _getSymbol(content)
  print('  Processed order. orderId:', orderId, 'brId:', brokerId, 'state:', state)
  send_sse('logprocessing', 'Processed order. orderId: ' + str(orderId) + ' brId: ' + str(brokerId) + ' state: ' + state)
  register_mc_raw_order(RawOrder(orderId, brokerId, strategyRef, action, category, generatedTs, finalTs, initialPrice, fillPrice, qty, fillQty, brokerProfile, account, symbol))


def processLogentry(logentry_ts, content):
  if _isStrategyIdentifier(content):
    _processStrategyIdentifier(logentry_ts, content)
  elif _isOrderEvent(content):
    _processOrderEvent(content)

def getOrders():
  global orders
  temp_orders = deepcopy(orders)
  orders = []
  return temp_orders

def getStrategies():
  global strategies
  temp_strategies = deepcopy(strategies)
  strategies = []
  return temp_strategies
