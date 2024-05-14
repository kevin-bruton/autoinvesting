from collections import namedtuple
from db.common import mutate_one, query_many, mutate_many, values_placeholder

subscription_fields = 'magicAccountId,accountId, magic'
Subscription = namedtuple('Subscription', subscription_fields)

def get_subscriptions ():
  sql = 'SELECT magicAccountId, accountId, magic FROM Subscriptions'
  return query_many(sql)

def update_subscriptions (account_id, magics):
  sql = 'DELETE FROM Subscriptions WHERE accountId = ?'
  mutate_many(sql, (account_id,))
  sql = 'INSERT INTO Subscriptions (magicAccountId, magic, accountId) VALUES (?,?,?)'
  values = [(f"{magic}_{account_id}", magic, account_id) for magic in magics]
  mutate_many(sql, values)

def save_subscription (subscription):
  sql = f"INSERT INTO Subscriptions ({subscription_fields}) VALUES ({values_placeholder(subscription_fields)})"
  return mutate_one(sql, subscription)

def get_accounts_subscriptions (account_id):
  sql = 'SELECT magic FROM Subscriptions WHERE accountId = ?'
  subscriptions = query_many(sql, (account_id,))
  magics = [s['magic'] for s in subscriptions]
  return magics

def get_accounts_subscribed_to_magic (magic):
  sql = 'SELECT accountId FROM Subscriptions WHERE magic = ?'
  results = query_many(sql, (magic,))
  return [r['accountId'] for r in results]
