from typing import Annotated
from fastapi import APIRouter, Header, Response
from pydantic import BaseModel
from fast.auth import generate_user_token

route = APIRouter()

@route.get("/version")
async def version():
    return {"api-version": "1.0.0"}

class LoginRequest(BaseModel):
    username: str
    passwd: str
  
class User(BaseModel):
    username: str
    firstname: str
    lastname: str
    accountType: str

@route.post('/authenticate') 
def authenticate_request(host: Annotated[str, Header()], credentials: LoginRequest, response: Response):
  print('host: ', host, 'credentials: ', credentials.username, credentials.passwd)
  auth_cookie_max_age_in_secs = 60 * 60 * 24 # 24 hours
  if not credentials or not credentials.username or not credentials.passwd:
    response.status_code = 401
    return {'error': 'Credentials not provided'}

  try:
    token, user_data = generate_user_token(credentials.username, credentials.passwd, host)
    response.set_cookie(key='ait', value=token, httponly=True, samesite='strict', max_age=auth_cookie_max_age_in_secs)
    return {'user' : user_data}
  except Exception as e:
    print('CAUGHT ERROR: ', e)
    response.status_code = 401
    return {'error': str(e)}

