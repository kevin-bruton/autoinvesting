from typing import Annotated
from fastapi import APIRouter, Response
from pydantic import BaseModel
from db.subscriptions import get_subscriptions

route = APIRouter()

@route.get('/subscriptions')
def get_subscriptions_request():
  return {'success': True, 'data': get_subscriptions()}
