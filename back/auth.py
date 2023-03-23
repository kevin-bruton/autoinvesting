from flask import Flask, request, jsonify
from db import get_user
from os import getenv
from datetime import datetime, timedelta
import jwt
from functools import wraps

TOKEN_EXPIRATION_MINS = 1440

def generate_user_token (username, password, host):
  user = get_user(username, password)
  print('generateUserToken:: got user: ', user)
  if user:
    token = jwt.encode({
          'username' : user['username'],
          'firstname': user['firstName'],
          'lastname': user['lastName'],
          'accountType': user['accountType'],
          'host': host,
          'exp' : datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRATION_MINS)
        },
        getenv('JWT_SECRET'),
        'HS256'
      )
    return token
  else:
    raise Exception('Invalid user credentials')

def validate_token (reqHeaders):
  token = None
  if 'Authorization' in reqHeaders:
    token = reqHeaders['Authorization'].split(' ')[1]
  if not token:
    raise Exception('Token missing')

  user = None
  try:
    user = jwt.decode(token, getenv('JWT_SECRET'), algorithms=["HS256"])
  except:
    raise Exception('Invalid token')

  # print('Decoded token: ', user)
  # print('User host and request host:', user['host'], reqHeaders['Host'])
  if user['host'] != reqHeaders['Host'] or reqHeaders['Host'] == 'localhost':
    raise Exception('Invalid token: wrong host')
  
  # check if expired
  if datetime.timestamp(datetime.utcnow()) > user['exp']:
    raise Exception('Token expired')
  return user

def token_required(f):
  @wraps(f)
  def decorator(*args, **kwargs):
    try:
      user = validate_token(request.headers)
    except Exception as e:
      return (jsonify({'error': str(e)}), 401)
    return f(user, *args, **kwargs)
  return decorator

def admin_only(f):
  @wraps(f)
  def decorator(*args, **kwargs):
    try:
      user = validate_token(request.headers)
    except Exception as e:
      return (jsonify({'error': str(e)}), 401)
    if user['accountType'] != 'admin':
      return (jsonify({'error': 'User does not have permission'}), 401)
    return f(user, *args, **kwargs)
  return decorator

