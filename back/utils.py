import quantstats as qs
from os import getenv
from requests import post
from os.path import join

stock = qs.utils.download_returns('FB')

def get_returns_series(balances):
  pass

def get_kpis(deposit, start_date, end_date, balances, profit):
  pass

def upload_to_dropbox (type, origin_foler, filename):
  file_origin = join(origin_foler, filename)
  file_destination = f'/{type}/{filename}'
  url = 'https://content.dropboxapi.com/2/files/upload'
  headers = {
    'Authorization': f"Bearer {getenv('DROPBOX_KEY')}",
    'Dropbox-API-Arg': '{"autorename":false,"mode":"add","mute":false,"path":"' + file_destination + '","strict_conflict":false}',
    'Content-Type': 'application/octet-stream'
  }
  print('DROPBOX HEADERS: ', headers)

  with open(file_origin, 'rb') as f:
    data = f.read()
    res = post(url=url, data=data, headers=headers)
    print('UPLOAD TO DROPBOX RESPONSE STATUS: ', res.status_code, res.text)
    