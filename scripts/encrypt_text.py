from os import getenv
import json
from dotenv import load_dotenv
load_dotenv()

from fast.routers.query import encrypt, decrypt

def do_encrypt():
  query = {
    "type": "query_one",
    "sql": """
        SELECT strategyRunId
        FROM StrategyRuns
        WHERE strategyId = ? AND accountId = ?
      """
  }

  encrypted_text = encrypt(query)
  print('Encrypted text:')
  print(encrypted_text)
  print('Decrypted text:')
  print(decrypt(encrypted_text))

def do_decrypt():
  encrypted_text = input('Enter encrypted text: ')
  print('Decrypted text:')
  print(decrypt(encrypted_text))
