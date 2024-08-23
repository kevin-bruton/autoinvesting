import json
from cryptography.fernet import Fernet
from typing import Annotated
from fastapi import APIRouter, Request, Response
from pydantic import BaseModel
from fast.query_handler import handle_query

route = APIRouter()

@route.post('/query')
async def query_request(request: Request):
  user = request.state.user
  print('User: ', user)
  data = await request.body()
  try:
    query_data = json.loads(data)
    print('query_data: ', query_data)
    query_name, values = query_data
  except Exception as e:
    print('Error decoding query data: ', e)
    return {'success': False }
  try:
    result = handle_query(user, query_name, values)
    print('query result: ', result)
    return {'success': True, 'data': result}
  except Exception as e:
    print('Error executing query: ', e)
    return {'success': False }
