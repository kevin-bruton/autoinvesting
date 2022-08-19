from os import getenv
import mysql.connector
from mysql.connector import pooling
import json
from datetime import datetime

cnx_pool = None

def init_connection_pool():
  db_config = {
    'host': getenv('DB_SERVERNAME'),
    'user': getenv('DB_USERNAME'),
    'password': getenv('DB_PASSWORD'),
    'database': getenv('DB_NAME')
  }
  return mysql.connector.pooling.MySQLConnectionPool(
    pool_name = "db_pool",
    pool_size = 32,
    pool_reset_session = True,
    **db_config
  )

def get_connection():
  global cnx_pool
  if not cnx_pool:
    cnx_pool = init_connection_pool()
  return cnx_pool.get_connection()

def authenticate_user (token, account_type, account_number):
  cnx = get_connection()
  acc_type = 'demo' if account_type == 'DEMO' else 'live'
  key_field = f'{acc_type}Key'
  acc_num_field = f'{acc_type}AccountNumber'
  subscriptions_field = f'{acc_type}Subscriptions'
  sql = f"SELECT {key_field}, {acc_num_field}, {subscriptions_field} FROM Users WHERE {key_field} = %s AND {acc_num_field} = %s"
  c = cnx.cursor(dictionary=True)
  c.execute(sql, (token, account_number))
  user = c.fetchone()
  return json.loads(user[subscriptions_field]) if user else []

