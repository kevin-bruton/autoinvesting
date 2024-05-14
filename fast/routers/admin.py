from typing import Annotated
from fastapi import APIRouter, Request, Response
from pydantic import BaseModel
from db.strategies import save_strategy
from fast.controllers import decommission_strategy, reactivate_strategy, save_new_strategies

from fast.strategies_csv import save_all_strategy_data, save_strategies_csv
from fast.utils import get_upload_folders

route = APIRouter()

class Strategy(BaseModel):
  strategyName: str
  magic: int
  symbols: list[str]
  timeframes: list[str]
  demoStart: str
  strategyWorkflow: str
  strategyDescription: str

@route.post('/strategies')
def save_strategy_request(strategy: Strategy):
  try:
    save_strategy(strategy)
    return {'message': 'Saved strategy successfully'}
  except Exception as e:
    error_msg = repr(e)
    if 'Duplicate entry' in error_msg:
      error_msg = error_msg[error_msg.find('Duplicate entry') : error_msg.find(' for key')]
    return {'error': error_msg}
  
@route.get('/strategy-decommission/{magic}')
def decommission_strategy_request(magic):
  try:
    decommission_strategy(magic)
    return {"result": "success"}
  except Exception as e:
    return {"error": repr(e)}

@route.get('/strategy-reactivate/{magic}')
def reactivate_strategy_request(magic):
  try:
    reactivate_strategy(magic)
    return {"result": "success"}
  except Exception as e:
    return {"error": repr(e)}

@route.post('/strategies-csv')
async def save_strategies_csv_request(request: Request):
  strategies_csv = await request.body()
  results = save_strategies_csv(strategies_csv)
  return results

@route.post('/strategies-json')
async def save_all_strategy_data_request(request: Request):
  all_strategy_data = await request.body()
  results = save_all_strategy_data(all_strategy_data)
  return results

""" upload_file is not defined
@route.post('/files')
def upload_file_request(request: Request):
  user = request.state.user
  try:
    upload_file(user, request)
    return (jsonify({'message': 'File uploaded successfully'}))
  except Exception as e:
    return (jsonify({'error': repr(e)}), 200) """

""" Revise this route. Examine bactest format etc.
@route.post('/backtest')
def save_backtest_request()):
  try:
    data = request.get_json()
    # add kpis to data ?
    save_backtest(data)
    return (jsonify({'message': 'Saved backtest successfully'}), 200)
  except Exception as e:
    print(repr(e))
    return(jsonify({'error': repr(e)}), 200) """

class NewStrategyUploadRequest(BaseModel):
  uploadFolder: str

@route.post('/save-new-strategies')
def save_new_strategies_request(uploadRequest: NewStrategyUploadRequest):
  try:
    result = save_new_strategies(uploadRequest.uploadFolder)
    return {'message': 'Saved new strategies successfully'}
  except Exception as e:
    print(repr(e))
    return {'error': repr(e)}

@route.get('/upload-folders')
def get_upload_folders_request():
  try:
    folders = get_upload_folders()
    return {'success': True, 'data': folders}
  except Exception as e:
    print(repr(e))
    return {'error': repr(e)}