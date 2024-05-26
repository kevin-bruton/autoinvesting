from datetime import datetime
from db2.common import query_one, mutate_one

def register_update (result):
  now = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
  sql = 'INSERT INTO Updates (updateTime,result) VALUES (?, ?);'
  return mutate_one(sql, (now, result))

def get_last_update ():
  sql = 'SELECT MAX(updateTime) FROM Updates'
  return query_one(sql)
