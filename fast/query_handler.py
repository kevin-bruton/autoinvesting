
from db.query import dbQuery
from db.users import get_users, get_users_accounts
from db.strategy_runs import get_account_strategyruns

def handle_query (user, query_name, values):
  match query_name:
    case 'get_users_accounts':
      account_ids = get_users_accounts(user['username'])
      return account_ids
    case 'get_account_strategies':
      account_id = values[0]
      strategies = get_account_strategyruns(account_id)
      return strategies
    case _:
      return 'Unknown query name'