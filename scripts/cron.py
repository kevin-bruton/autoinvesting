import schedule
import time
from scripts.update_from_mt import run_update_from_mt
from scripts.wifi_connector import check_connection

def run_cron():
  update_freq_secs = 60 * 60
  print('\nStarting cron jobs...\n')

  schedule.every(update_freq_secs).seconds.do(run_update_from_mt)
  schedule.every(60).seconds.do(check_connection)

  while True:
    schedule.run_pending()
    time.sleep(1)