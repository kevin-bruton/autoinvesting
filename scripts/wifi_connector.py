import requests
import winwifi
from datetime import datetime

wifi_names = ['Oz2', 'Factory']

def _log(txt):
  time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  with open(f"logs/wifi.log", 'a') as f:
    f.write(f"{time_str} {txt}\n")

def _get_last_wifi_status():
  try:
    with open(f'logs/wifi_connection_status.txt', 'r') as f:
      return f.read().strip().split(';')
  except:
    return 'None'
  
def _save_wifi_status(status):
  time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  with open(f'logs/wifi_connection_status.txt', 'w') as f:
    f.write(f'{time_str};{status}')

def _get_wifi_connected_to():
  interfaces = winwifi.WinWiFi.get_connected_interfaces()
  if not interfaces or len(interfaces) == 0:
    return 'None'
  return interfaces[0].ssid

def _test_connection():
  try:
    resp = requests.get('http://www.google.com', timeout=2)
    if resp.status_code != 200:
      _log('Failed http test. Connection status code:', resp.status_code)
    else:
      # _log('Successful http test')
      pass
    return resp.status_code == 200
  except:
    _log('Failed http test. Connection error.')
    return False
  
def _connect_to_wifi(ssid):
  winwifi.WinWiFi.disconnect()
  try:
    winwifi.WinWiFi.connect(ssid)
  except Exception as e:
    print('Failed to connect to ', ssid, repr(e))
    return False
  return _test_connection()

def check_connection():
  #print(datetime.now(), 'Checking wifi connection...')
  last_wifi_change, last_status = _get_last_wifi_status()
  current_wifi = _get_wifi_connected_to()
  if last_status != current_wifi:
    _save_wifi_status(current_wifi)
    _log(f'Wifi status changed from {last_status} to {current_wifi}')
  else:
    last_wifi_change_dt = datetime.strptime(last_wifi_change, '%Y-%m-%d %H:%M:%S')
    time_since_last_change = (datetime.now() - last_wifi_change_dt).total_seconds()
    if time_since_last_change > 60*60 and current_wifi != wifi_names[0]:
        _log(f'Not connected to primary wifi for more than an hour. Trying to connect to {wifi_names[0]}')
        _connect_to_wifi(wifi_names[0])
        current_wifi = _get_wifi_connected_to()
        _save_wifi_status(current_wifi)
        if last_status != current_wifi:
          _log(f'Wifi status changed from {last_status} to {current_wifi}')
        else:
          _log(f'Failed to connect to {wifi_names[0]}')
  if not _test_connection():
    _log('Failed http test. Now trying to connect to ' + wifi_names[0])
    if not _connect_to_wifi(wifi_names[0]):
      _log('Failed to connect to ' + wifi_names[0] + '. Trying to connect to ' + wifi_names[1])
      if not _connect_to_wifi(wifi_names[1]):
        _log('Failed to connect to ' + wifi_names[1])
        return False
      else:
        _log('Connected to ' + wifi_names[1])
    else:
      _log('Connected to ' + wifi_names[0])
