from collections import namedtuple
from db.common import query_many, query_one, mutate_one,values_placeholder

user_fields = 'accountType, username, passwd, email, firstName, lastName, city, country'
User = namedtuple('User', user_fields, defaults=(None, None))

def get_user (username, passwd) -> User:
  sql = "SELECT * FROM Users WHERE username = ? AND passwd = ?"
  return query_one(sql, (username, passwd))

def get_users () -> list[User]:
  sql = 'SELECT username, passwd, email, firstName, lastName, city, country, accountType FROM Users'
  return query_many(sql)

def get_users_accounts (username: str) -> list[str]:
  sql = 'SELECT accountId, name, platform, platformDir FROM Accounts WHERE username = ? AND platformDir IS NOT NULL'
  return query_many(sql, (username,))

def save_user (user:User) -> int:
  sql = f"INSERT INTO Users ({user_fields}) VALUES ({values_placeholder(user_fields)})"
  return mutate_one(sql, user)
