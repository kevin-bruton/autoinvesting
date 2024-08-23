
from db.query import dbQuery
from db.users import get_users, get_users_accounts

def handle_query (user, query_name, values):
  match query_name:
    case 'get_user_accounts':
      account_ids = get_users_accounts(user['username'])
      return account_ids