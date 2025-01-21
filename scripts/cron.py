import schedule
import time
from scripts.update_from_mt import run_update_from_mt
import platform

MT_UPDATE_FREQ_MINS = 60
CHECK_WIFI_FREQ_MINS = 1

if platform.system() == 'Windows':
  from scripts.wifi_connector import check_connection

def run_cron():
  print('\nStarting cron jobs...\n')

  schedule.every(MT_UPDATE_FREQ_MINS).minutes.do(run_update_from_mt)
  if platform.system() == 'Windows':
    schedule.every(CHECK_WIFI_FREQ_MINS).minutes.do(check_connection)

  while True:
    schedule.run_pending()
    time.sleep(1)