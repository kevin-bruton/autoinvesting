from collections import namedtuple
from db1.common import mutate_many, mutate_one, query_many, query_one, datetime_fmt, values_placeholder

order_fields = 'orderId, masterOrderId, accountId, magic, symbol, orderType, openTime, openPrice, size, comment, sl, tp, status'
Order = namedtuple('Order', order_fields)

def get_orders ():
  sql = f'SELECT {order_fields} FROM Orders'
  return query_many(sql)

def get_order (order_id):
  sql = f"SELECT {order_fields} FROM Orders WHERE orderId = ?"
  row = query_one(sql, (order_id,))
  return row

def get_account_orders (account_id):
  sql = 'SELECT * FROM Orders WHERE accountId = ?'
  orders = query_many(sql, (account_id,))
  return [{**o, **{
    'openTime': o['openTime'].strftime(datetime_fmt),
    'size': float(o['size'])
  }} for o in orders]

def get_corresponding_orderid (masterOrderId, accountId):
  sql = 'SELECT orderId FROM Orders WHERE masterOrderId = ? AND accountId = ?'
  row = query_one(sql, (masterOrderId, accountId))
  return row['orderId'] if row != None else None

def save_order (order):
  sql = f"INSERT INTO Orders ({order_fields}) VALUES ({values_placeholder(order_fields)})"
  return mutate_one(sql, order)

def update_order_status (orderId, status):
  sql = 'UPDATE Orders SET status = ? WHERE orderId = ?'
  return mutate_one(sql, (status, orderId))

def delete_order (order_id):
  sql = 'DELETE From Orders WHERE orderId = ?'
  return mutate_many(sql, (order_id,))
