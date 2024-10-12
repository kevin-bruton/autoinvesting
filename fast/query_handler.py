
import asyncio
from concurrent.futures import ThreadPoolExecutor
from db.query import dbQuery
from db.trades import get_strategys_backtest_trades, get_strategys_combined_trades, get_strategys_live_trades
from db.users import get_users, get_users_accounts
from db.strategy_runs import get_account_strategyruns
from fast.controllers import calc_correlation_matrix, get_portfolio_evaluation, get_strategy_detail
from mc.log_analysis.read_logs import process_last_logentries

async def handle_query (user, query_name, values):
  match query_name:
    case 'get_users_accounts':
      account_ids = get_users_accounts(user['username'])
      return account_ids
    case 'get_account_strategies':
      account_id = values[0]
      strategies = get_account_strategyruns(account_id)
      return strategies
    case 'get_strategyrun_trades':
      strategyrun_id = values[0]
      trades = dbQuery(
        'query_many',
        'SELECT orderId, symbol, orderType, openTime, closeTime, size, balance, profit, sl, tp, swap, commission FROM Trades WHERE strategyRunId = ?',
        [strategyrun_id]
      )
      return trades
    case 'get_strategy_combined_trades':
      strategyId, accountId = values
      trades = get_strategys_combined_trades(strategyId, accountId)
      return trades
    case 'get_strategy_live_trades':
      strategyId, accountId = values
      trades = get_strategys_live_trades(strategyId, accountId)
      return trades
    case 'get_strategy_backtest_trades':
      strategyId = values[0]
      trades = get_strategys_backtest_trades(strategyId)
      return trades
    case 'get_strategy_detail':
      return get_strategy_detail(strategyId=values[0], accountId=values[1])
    case 'get_account_strategyruns':
      account_id = values[0]
      strategyruns = get_account_strategyruns(account_id)
      return strategyruns
    case 'get_portfolio_evaluation':
      data_type, account_id, strategy_ids = values
      return get_portfolio_evaluation(data_type, account_id, strategy_ids)
    case 'get_correlation_matrix':
      account_id,  data_type, timeframe, strategy_ids = values
      return calc_correlation_matrix(account_id, data_type, timeframe, strategy_ids)
    case 'get_strategyrunid':
      strategy_id, account_id = values
      return dbQuery(
        'query_one',
        'SELECT strategyRunId FROM StrategyRuns WHERE strategyId = ? AND accountId = ?',
        [strategy_id, account_id]
      )
    case 'save_mc_latest_orders':
      print('save_mc_latest_orders: ', values)
      loop = asyncio.get_event_loop()
      with ThreadPoolExecutor() as pool:
        await loop.run_in_executor(pool, process_last_logentries)
      return {'message': 'Started processing latest MC log entries'}
      
    case _:
      return 'Unknown query name'