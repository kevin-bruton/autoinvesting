from datetime import datetime
from collections import namedtuple
from db.common import query_many, query_one, mutate_one, values_placeholder, datetime_fmt

raw_order_fields = 'orderId, brokerId, strategyRef, action, category, generatedDt, finalDt, initialPrice, fillPrice, qty, fillQty, brokerProfile, account, symbol'
RawOrder = namedtuple('RawMcOrder', raw_order_fields)

def register_mc_raw_order (raw_order):
  sql = f"INSERT INTO RawMcOrders ({raw_order_fields}) VALUES ({values_placeholder(raw_order_fields)})"
  return mutate_one(sql, raw_order)