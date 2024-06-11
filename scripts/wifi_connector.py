import requests
import winwifi
from datetime import datetime

def test_connection():
  try:
    resp = requests.get('http://www.google.com', timeout=2)
    if resp.status_code != 200:
      print('Failed to connect to google.com. Connection status code:', resp.status_code)
    return resp.status_code == 200
  except:
    print('Failed to connect to google.com')
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
    print(datetime.now(), 'No internet connection. Trying to connect to ', wifi_names[0])
    if not connect_to_wifi(wifi_names[0]):
      print(datetime.now(), 'Failed to connect to ', wifi_names[0], '. Trying to connect to ', wifi_names[1])
      if not connect_to_wifi(wifi_names[1]):
        print(datetime.now(), 'Failed to connect to ', wifi_names[1])
        return False
      else:
        print(datetime.now(), 'Connected to ', wifi_names[1])
    else:
      print(datetime.now(), 'Connected to ', wifi_names[0])