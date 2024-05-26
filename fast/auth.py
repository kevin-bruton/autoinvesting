from os import getenv
from typing import Annotated, Union
from fastapi import Cookie, Depends, HTTPException, Request
import jwt

from db2.users import get_user

def generate_user_token (username, password, host):
  user = get_user(username, password)
  print('generateUserToken:: got user: ', user)
  if user:
    token = jwt.encode({
          'username' : user['username'],
          'firstname': user['firstName'],
          'lastname': user['lastName'],
          'accountType': user['accountType'],
          'host': host
        },
        getenv('JWT_SECRET'),
        'HS256'
      )
    user_data = {'username' : user['username'], 'firstname': user['firstName'], 'lastname': user['lastName'], 'accountType': user['accountType']}
    return token, user_data
  else:
    raise Exception('Invalid user credentials')

async def is_member(request: Request, ait: Annotated[Union[str, None], Cookie()] = None):
  if not ait:
    raise HTTPException(status_code=401, detail='Token missing')
  try:
     user = jwt.decode(ait, getenv('JWT_SECRET'), algorithms=["HS256"])
  except:
    raise HTTPException(status_code=401, detail='Invalid token')
  request.state.user = user
  return user

async def is_admin(user = Depends(is_member)):
  if user['accountType'] != 'admin':
    raise HTTPException(status_code=401, detail='User does not have permission')
  return user

""" Example of only validation on a route:
@route.get('/validate', dependencies=[Depends(logged_in)])
def validate_request():
  return {'result': 'ok'}
"""
""" Example of validation and user info on a route:
@route.get('/validate')
def validate_request(user = Depends(logged_in)):
  return { 'user': user}
"""