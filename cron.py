import schedule
import time
from update_from_mt import run_update_from_mt

update_freq_secs = 60 * 60
print('\nStarting cron jobs...\n')

schedule.every(update_freq_secs).seconds.do(run_update_from_mt)

while True:
  schedule.run_pending()
  time.sleep(1)