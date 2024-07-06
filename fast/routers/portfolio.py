import traceback
from typing import Annotated, Dict
from fastapi import APIRouter, Request, Response
from pydantic import BaseModel
from fast.controllers import apply_position_sizing, calc_correlation_matrix, get_account_logs

route = APIRouter()

class CorrelationMatrixData(BaseModel):
  strategyIds: list[int]
  dataType: str
  timeframe: str

@route.post('/correlation-matrix')
def get_correlation_matrix(data: CorrelationMatrixData):
  matrix = calc_correlation_matrix(data.strategyIds, data.dataType, data.timeframe)
  return Response(content=matrix)

@route.post('/position-sizing')
def apply_positon_sizing_request(account_id: str, sizes: Dict[int, float]):
  try:
    apply_position_sizing(account_id, sizes)
    return {'result': 'success'}
  except Exception as e:
    print(e, traceback.format_exc())
    return {'error': repr(e)}
