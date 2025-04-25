from db.strategies import get_strategies
from db.strategy_runs import get_strategyrunids
from db.trades import get_strategyrunid_trades

def save_all_trades_to_file ():
  strategies = get_strategies()
  for strategy in strategies:
    strategy_id = strategy['strategyId']
    if strategy_id == '0': continue
    strategy_runs = get_strategyrunids(strategy_id)
    for strategy_run_id in strategy_runs:
      trades = get_strategyrunid_trades(strategy_run_id)
      filename = f'./data/{strategy_id}_{strategy_run_id}_trades.csv'
      with open(filename, 'w') as f:
        f.write('orderId,strategyRunId,symbol,orderType,openTime,closeTime,openPrice,closePrice,size,profit,balance,closeType,comment,sl,tp,swap,commission\n')
        for t in trades:
          #line = ','.join([str(v) for v in dict(trade).values()]) + '\n'
          line = f'{t['orderId']},{t['strategyRunId']},{t['symbol']},{t['orderType']},{t['openTime']},{t['closeTime']},{t['openPrice']},{t['closePrice']},{t['size']},{t['profit']},{t['balance']},{t['closeType']},{t['comment']},{t['sl']},{t['tp']},{t['swap']},{t['commission']}\n'
          f.write(line)
      print(f'Saved trades to {filename}')
