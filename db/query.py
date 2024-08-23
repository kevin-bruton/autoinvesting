from datetime import datetime
from collections import namedtuple
from db.common import mutate_many, mutate_one, query_many, query_one, values_placeholder

def dbQuery (type, sql, values):
  if type == 'query_one':
    return query_one(sql, tuple(values))
  elif type == 'query_many':
    return query_many(sql, tuple(values))
  elif type == 'mutate_one':
    return mutate_one(sql, tuple(values))
  elif type == 'mutate_many':
    return mutate_many(sql, tuple(values))
