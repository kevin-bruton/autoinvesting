from typing import Annotated
from fastapi import APIRouter, Response
from pydantic import BaseModel
from db.orders import get_orders
from db.strategies import get_strategy_detail, get_strategy_summaries, get_strategies
from fast.controllers import calc_correlation_matrix

route = APIRouter()

@route.get('/strategies')
def get_strategies_request():
  return {'success': True, 'data': get_strategies()}

@route.get('/orders')
def get_orders_request():
  return {'success': True, 'data': get_orders()}

@route.get('/trades')
def get_trades():
  return {'success': True, 'data': get_trades()}

@route.get('/strategies/summary')
def get_strategies_summaries_request():
  return {'success': True, 'data': get_strategy_summaries()}


@route.get('/strategies/{strategy_id}')
def get_strategy_request(strategy_id: str):
  """ if strategy_id == 'all':
    try:
      strategies = get_all_strategy_data_as_csv()
      return strategies
    except Exception as e:
      return { 'error': repr(e) }
  else: """
  try:
    strategy = get_strategy_detail(strategy_id)
    return strategy
  except Exception as e:
    return { 'error': repr(e) }
