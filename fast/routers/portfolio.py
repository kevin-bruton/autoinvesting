import traceback
from typing import Annotated, Dict, List
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
class StrategyPositionSize(BaseModel):
  strategyId: str
  positionSize: float

# DEPRECATED: use /query instead with "generate_mt_templates"
@route.post('/position-sizing')
def apply_positon_sizing_request(accountId: str, strategyPositionSizes: List[StrategyPositionSize]):
  print(f'apply_positon_sizing_request: {accountId}')
  try:
    apply_position_sizing(accountId, strategyPositionSizes)
    return {'result': 'success'}
  except Exception as e:
    print(e, traceback.format_exc())
    return {'error': repr(e)}
