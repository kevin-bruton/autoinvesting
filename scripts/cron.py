import schedule
import time
from scripts.update_from_mt import run_update_from_mt
import platform

MT_UPDATE_FREQ_SECS = 60 * 60
CHECK_WIFI_FREQ_SECS = 60

if platform.system() == 'Windows':
  from scripts.wifi_connector import check_connection

def run_cron():
  print('\nStarting cron jobs...\n')

  schedule.every(MT_UPDATE_FREQ_SECS).seconds.do(run_update_from_mt)
  if platform.system() == 'Windows':
    schedule.every(CHECK_WIFI_FREQ_SECS).seconds.do(check_connection)

  while True:
    schedule.run_pending()
    time.sleep(1)