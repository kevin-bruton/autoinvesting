import requests
import winwifi
from datetime import datetime

def log(txt):
  time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  with open(f"logs/master.log", 'a') as f:
    f.write(f"{time_str} {txt}\n")

def test_connection():
  try:
    resp = requests.get('http://www.google.com', timeout=2)
    if resp.status_code != 200:
      log('Failed http test. Connection status code:', resp.status_code)
    return resp.status_code == 200
  except:
    log('Failed http test. Connection error.')
    return False
  
def connect_to_wifi(ssid):
  winwifi.WinWiFi.disconnect()
  try:
    winwifi.WinWiFi.connect(ssid)
  except Exception as e:
    print('Failed to connect to ', ssid, repr(e))
    return False
  return test_connection()

def check_connection():
  wifi_names = ['Oz2', 'Factory']
  if not test_connection():
    log('Failed http test. Now trying to connect to ' + wifi_names[0])
    if not connect_to_wifi(wifi_names[0]):
      log('Failed to connect to ' + wifi_names[0] + '. Trying to connect to ' + wifi_names[1])
      if not connect_to_wifi(wifi_names[1]):
        log('Failed to connect to ' + wifi_names[1])
        return False
      else:
        log('Connected to ' + wifi_names[1])
    else:
      log('Connected to ' + wifi_names[0])