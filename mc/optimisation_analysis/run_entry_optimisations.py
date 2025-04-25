
from collections import namedtuple
import math
import random
import pywinauto, time
from pywinauto.application import Application
from pywinauto.keyboard import send_keys
from pywinauto import mouse

# The program must be started from this directory for it to be found:
multicharts_exec_file = r'C:/Multicharts/MultiCharts64.exe'
reports_dir = './entries/' ##### For now, you must have already saved a report to the directory where you want to save them !!!!

Chart = namedtuple('Chart', ['symbol', 'strategy_name', 'timeframes', 'num_contracts'])

class Multicharts:
  def __init__(self, multicharts_path):
    print('Mulitcharts path:', multicharts_path)
    self.app = Application(backend='win32').connect(path=multicharts_path)
    self.app.top_window().set_focus()
    time.sleep(1)

  def open_new_workspace(self):
    self.app.top_window().set_focus()
    send_keys('^n')  # Ctrl+N
    time.sleep(1)
  
  def new_chart(self, data_source, instrument, timeframes, tf_unit, days_back):
    self.app.top_window().set_focus()
    send_keys('{INSERT}')  # Ctrl+T
    time.sleep(1)
    self.select_data_source(data_source)
    self.select_instrument(instrument)
    self.select_settings_tab(timeframes[0], tf_unit, days_back)

    if len(timeframes) > 1:
      send_keys('{F5}')
      time.sleep(1)
      self.select_settings_tab(timeframes[1], tf_unit, days_back)

  def print_control_ids(self):
    self.app.top_window().print_control_identifiers()
    time.sleep(1)
  
  def get_app(self):
    return self.app
  
  ''' In Format Instrument Dialog '''
  def select_data_source(self, data_source):
    time.sleep(1)
    self.app['Format Instrument']['Data Source:ComboBox'].click()
    time.sleep(1)
    self.app['Format Instrument']['Data Source:ComboBox'].select(data_source)
    time.sleep(1)
    send_keys('{ENTER}')

  def select_instrument(self, instrument):
    time.sleep(1)
    self.app['Format Instrument'].ComboBox2.Edit.click()
    time.sleep(1)
    #self.app['Format Instrument']['Instrument:ComboBox'](instrument)
    print('Typing instrument...')
    send_keys(instrument)
    time.sleep(1)
    send_keys('{TAB}')

  def select_settings_tab(self, timeframe, tf_unit, days_back):
    dialog = self.app.Dialog
    self.app.top_window().set_focus()
    time.sleep(1)
    #self.app['Format Instrument'].Settings.click()
    dialog.Cancel.set_focus()
    time.sleep(1)
    send_keys('{TAB}')
    send_keys('{RIGHT}')
    send_keys('{TAB}')
    send_keys('{TAB}')
    send_keys(timeframe)
    send_keys('{TAB}')
    dialog.ComboBox2.click() #.print_control_identifiers()
    dialog.ComboBox2.select(tf_unit)
    time.sleep(1)
    send_keys('{ENTER}')
    time.sleep(1)
    dialog.RadioButton0.click()
    time.sleep(1)
    send_keys('{TAB}')
    send_keys(days_back)
    dialog.ComboBox6.click()
    dialog.ComboBox6.select('Days Back')
    send_keys('{ENTER}')
    dialog.OKButton.click()
    time.sleep(1)
    #self.app['Format Instrument'].TabControlSettings.click()

  def insert_signal(self, strategy_name, num_contracts=1):
    self.app.top_window().set_focus()
    time.sleep(1)
    send_keys('%i')
    time.sleep(1)
    send_keys('l')
    time.sleep(1)

    dialog = self.app.Dialog
    dialog.move_window(x=0, y=0)
    mouse.click(coords=(100,60))
    mouse.scroll(coords=(100,125), wheel_dist=400)
    mouse.click(coords=(100,125))
    items = dialog.List.texts()
    strat_idx = -1
    for itemIdx, item in enumerate(items):
      if item == strategy_name:
        strat_idx = itemIdx
        break
    if strat_idx == -1:
      print('Strategy not found:', strategy_name)
      return
    strat_num = math.floor(strat_idx / 2)
    print('Strategy number:', strat_num)
    send_keys('{DOWN}' * strat_num)
    time.sleep(1)
    send_keys('{ENTER}')

    # Set contracts on chosen signal
    time.sleep(1)
    dialog = self.app['Format Objects']
    dialog.move_window(x=0, y=0)
    mouse.click(coords=(285,55)) # Signals tab
    time.sleep(3)
    mouse.move(coords=(638,115)) # Config button
    time.sleep(1)
    mouse.click(coords=(638,115)) # Config button
    time.sleep(1)

    dialog = self.app.Dialog
    dialog.move_window(x=0, y=0)
    mouse.click(coords=(22,55)) # Input tab
    mouse.click(coords=(230,150)) # Select first input value (numContracts)
    time.sleep(1)
    send_keys(str(num_contracts))
    time.sleep(1)
    send_keys('{TAB}')
    dialog.OKButton.click()
    
    dialog = self.app['Format Objects']
    mouse.click(coords=(855,485))
    
    
    time.sleep(1)
    
def run(start_entry_num=1, end_entry_num=35):
  mc = Multicharts(multicharts_path=multicharts_exec_file)
  #mc.menu_select('Format->Optimize Strategy')
  #mc.get_app().top_window().print_control_identifiers()

  app = mc.get_app()
  app.top_window().set_focus()
  app.top_window().move_window(x=0, y=0)
  time.sleep(1)

  # run optimisations
  for entry_num in range(start_entry_num, end_entry_num+1):
    print(f"Opimising entry {entry_num}/{end_entry_num}...")
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
    send_keys(str(entry_num))
    for _ in range(4):
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
    send_keys(f'entry_{entry_num}.csv')
    send_keys('{TAB}')
    for _ in range(3):
      send_keys('{DOWN}')
    send_keys('{ENTER}')
    for _ in range(2):
      send_keys('{TAB}')
    send_keys('{ENTER}')
    time.sleep(2)
    send_keys('%{F4}') # Close the optimisation report

  print('Done!')
  time.sleep(3)

if __name__ == '__main__':
  run()
#mc.print_control_ids()
