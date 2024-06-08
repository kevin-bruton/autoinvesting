from typing import Annotated
from fastapi import APIRouter, Response
from pydantic import BaseModel
import db

route = APIRouter()

@route.get('/strategyrun/{strategy_run_id}/trades')
def get_strategies_request(strategy_run_id: str):
  return {'success': True, 'data': db.get_strategyrun_trades(strategy_run_id)}
