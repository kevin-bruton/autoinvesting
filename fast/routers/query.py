from os import getenv
import base64
import json
from cryptography.fernet import Fernet
from typing import Annotated
from fastapi import APIRouter, Request, Response
from pydantic import BaseModel
from db.query import query

route = APIRouter()

#encrypt = lambda x: [(ord(c) + encrypt_key) for c in list(x)]
#decrypt = lambda x: ''.join([chr(i - encrypt_key) for i in x])
def encrypt(query: object) -> str:
  encrypt_key = getenv('ENCRYPT_KEY')
  if (len(encrypt_key) != 32):
    print('*** ERROR: ENCRYPT_KEY_INT must be 32 characters long. The provided key is ', len(encrypt_key), ' characters long.')
    return ''
  
  fernet_key = base64.urlsafe_b64encode(encrypt_key.encode('utf-8'))
  fernet = Fernet(fernet_key)
  return fernet.encrypt(json.dumps(query).encode('utf-8')).decode('utf-8')

def decrypt(cypher_txt: str) -> str:
  encrypt_key = getenv('ENCRYPT_KEY')
  if (len(encrypt_key) != 32):
    print('*** ERROR: ENCRYPT_KEY_INT must be 32 characters long. The provided key is ', len(encrypt_key), ' characters long.')
    return ''
  fernet_key = base64.urlsafe_b64encode(encrypt_key.encode('utf-8'))
  fernet = Fernet(fernet_key)
  query_obj =  json.loads(fernet.decrypt(cypher_txt).decode('utf-8'))
  return query_obj['type'], query_obj['sql']

@route.post('/query')
async def query_request(request: Request):
  user = request.state.user
  print('User: ', user)
  data = await request.body()
  try:
    #query_data = json.loads(base64.b64decode(data).decode('utf-8'))
    query_data = json.loads(data)
    print('query_data: ', query_data)
    type, sql, values = query_data #decrypt(query_data['query'])
    # values = query_data['values']
  except Exception as e:
    print('Error decoding query data: ', e)
    return {'success': False }
  print('Query. Type: ', type, ' SQL: ', sql, ' Values: ', values)
  try:
    result = query(type, sql, values)
    return {'success': True, 'data': result}
  except Exception as e:
    print('Error executing query: ', e)
    return {'success': False }
