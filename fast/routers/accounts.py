from typing import Annotated
from fastapi import APIRouter, Request, Response
from pydantic import BaseModel
from db2.accounts import get_accounts
from db2.orders import get_account_orders
#from db2.subscriptions import update_subscriptions
from db2.trades import get_account_trades
from db2.users import get_users, get_users_account_ids
from db2.updates import get_last_update
from fast.controllers import get_account_logs

from fast.utils import get_upload_folders

route = APIRouter()

@route.get('/validate')
def validate_request(request: Request):
  user = request.state.user
  return {'success': True, 'data': user}

@route.get('/users')
def get_users_request():
  return {'success': True, 'data': get_users()}

@route.get('/accounts')
def get_accounts_request():
  return {'success': True, 'data': get_accounts()}

@route.get('/user/accounts')
def get_users_accounts_request(request: Request):
  user = request.state.user
  account_ids = get_users_account_ids(user['username'])
  return {'success': True, 'data': account_ids }

@route.get('/account/{account_id}/orders')
def get_account_orders_request(account_id: str):
  orders = get_account_orders(account_id)
  return {'success': True, 'data': orders}

@route.get('/api/account/{account_id}/trades')
def get_accounts_trades(account_id: str):
  trades = get_account_trades(account_id)
  return {'success': True, 'data': trades}

@route.get('/account/{account_id}/logs')
def get_account_logs_request(account_id: str):
  log = get_account_logs(account_id)
  return log

@route.get('/account/{account_id}/connection-status')
def get_account_connection_status(account_id: str):
  status = get_account_connection_status(account_id)
  return {'success': True, 'data': status}

class SubscriptionRequest(BaseModel):
  magics: list[int]

""" @route.post('/account/<account_id>/subscribe')
def subscribe_to_strategies(account_id: str, magics: SubscriptionRequest):
  try:
    update_subscriptions(account_id, magics)
    return {'success': True}
  except Exception as e:
    return {'error': repr(e)}
 """
@route.get('/updates/last')
def get_last_update_request():
  try: 
    last_update = get_last_update()
    return { 'success': True, 'data': last_update['MAX(updateTime)'] }
  except Exception as e:
    return { 'error': repr(e) }
