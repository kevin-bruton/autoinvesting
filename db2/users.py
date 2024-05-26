from collections import namedtuple
from db2.common import query_many, query_one, mutate_one,values_placeholder

user_fields = 'accountType, username, passwd, email, firstName, lastName, city, country'
User = namedtuple('User', user_fields, defaults=(None, None))

def get_user (username, passwd) -> User:
  sql = "SELECT * FROM Users WHERE username = ? AND passwd = ?"
  return query_one(sql, (username, passwd))

def get_users () -> list[User]:
  sql = 'SELECT username, passwd, email, firstName, lastName, city, country, accountType FROM Users'
  return query_many(sql)

def get_users_account_ids (username: str) -> list[str]:
  sql = 'SELECT accountId FROM Accounts WHERE username = ?'
  return [a['accountId'] for a in query_many(sql, (username,))]

def save_user (user:User) -> int:
  sql = f"INSERT INTO Users ({user_fields}) VALUES ({values_placeholder(user_fields)})"
  return mutate_one(sql, user)
