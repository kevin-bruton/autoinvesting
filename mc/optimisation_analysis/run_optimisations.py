
from collections import namedtuple
import math
import random
import pywinauto, time
from pywinauto.application import Application
from pywinauto.keyboard import send_keys
from pywinauto import mouse

"""
This script is used to run a series of entry optimisations in Multicharts.
For each optimization run, it will go through the range of values specified for the first input.
The strategy must be generating random values for each run.

The first input is the one that will be incremented by one each time the optimisation is run.
The second input must be the number of strategies to generate for each optimisation run.

"""
# The program must be started from this directory for it to be found:
multicharts_exec_file = r'C:/Multicharts/MultiCharts64.exe'
reports_dir = 'C:/Users/kevin/autoinvesting/mc/optimisation_analysis/es_60_long_tf_var0_10/'
start_num = 0
end_num = 10
num_strategies_per_optimisation = 500

class Multicharts:
  def __init__(self, multicharts_path):
    print('Mulitcharts path:', multicharts_path)
    self.app = Application(backend='win32').connect(path=multicharts_path)
    self.app.top_window().set_focus()
    time.sleep(1)
  
  def get_app(self):
    return self.app
    
def run():
  mc = Multicharts(multicharts_path=multicharts_exec_file)
  #mc.menu_select('Format->Optimize Strategy')
  #mc.get_app().top_window().print_control_identifiers()

  app = mc.get_app()
  app.top_window().set_focus()
  app.top_window().move_window(x=0, y=0)
  time.sleep(1)

  # run optimisations
  for current_num in range(start_num, end_num+1):
    print(f"Opimising value {current_num}/{end_num}...")
    mouse.click(coords=(210,50)) # Menu -> Format
    time.sleep(1)
    for i in range(8):
      send_keys('{DOWN}')
    send_keys('{ENTER}')
    time.sleep(1)
    send_keys('{ENTER}')
    time.sleep(1)
    app.top_window().set_focus()
    time.sleep(1)
    for _ in range(4):
      send_keys('{TAB}')
    send_keys(str(current_num))
    for _ in range(2):
      send_keys('{TAB}')
    send_keys("1") # Set the first input to 1
    send_keys('{TAB}')
    send_keys(str(num_strategies_per_optimisation))
    for _ in range(7):
      send_keys('+{TAB}')
    send_keys('{ENTER}')
    # Optimisation should be running now...
    time.sleep(4)
    app.top_window().set_focus()
    dialog = app['Optimization Progress']
    dialog.wait_not('visible', timeout=60*60) # wait for 1 hour max for the optimisation to finish
    time.sleep(4)
    app.top_window().set_focus()
    app.top_window().move_window(x=0, y=0)
    mouse.click(coords=(60,65)) # Save results
    time.sleep(3)
    send_keys(f'optimisation_{current_num}.csv') # input filename
    send_keys('{TAB}')
    for _ in range(3):
      send_keys('{DOWN}')
    send_keys('{ENTER}') # select csv file format
    for _ in range(6):
      send_keys('{TAB}')
    send_keys('{ENTER}')
    send_keys(reports_dir) # input directory to save to
    send_keys('{ENTER}')
    for _ in range(10):
      send_keys('{TAB}')
    send_keys('{ENTER}') # select save button
    time.sleep(2)
    send_keys('%{F4}') # Close the optimisation report

  print('Done!')
  time.sleep(3)

if __name__ == '__main__':
  run()
#mc.print_control_ids()
