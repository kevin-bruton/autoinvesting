
from collections import namedtuple
import math
import random
import pywinauto, time
from pywinauto.application import Application
from pywinauto.keyboard import send_keys
from pywinauto import mouse

Chart = namedtuple('Chart', ['symbol', 'strategy_name', 'timeframes', 'num_contracts'])

class Multicharts:
  def __init__(self, multicharts_path):
    print('Mulitcharts path:', multicharts_path)
    self.app = Application().connect(path=multicharts_path)
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
    mc.select_data_source(data_source)
    mc.select_instrument(instrument)
    mc.select_settings_tab(timeframes[0], tf_unit, days_back)

    if len(timeframes) > 1:
      send_keys('{F5}')
      time.sleep(1)
      mc.select_settings_tab(timeframes[1], tf_unit, days_back)

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
    
    
charts_defn = []
print('Load Titan Portfolio into Multicharts')
print('Requirements:')
print(' - Chart symbols must be added (the continuous contracts)')
print(' - Strategies must be compiled and available')
print(' - Strategy names must be of the format {symbol}_{sub_cat}_{origin}_{num_id}_{root_symbol}_{timeframe}[_{timeframe_data2}]')
print('     eg. CL_TOP_UA_195_CL_15_1440 or EC_TOP_UA_196_EC_5')

print('\nReading Titan Portfolio from file "titan_portfolio.txt"...')
count = 0
with open('mc/automation/titan_portfolio.txt', 'r') as f:
  for line in f:
    count += 1
    #if count > 1: continue
    parts = line.split('\t')
    if len(parts) == 3:
        symbol = '@' + parts[1][:2]
        strategy_name = parts[1][3:]
        timeframes =  strategy_name.split('_')[4:6]
        num_contracts = parts[2].split('(')[0].strip()
        charts_defn.append(Chart(symbol, strategy_name, timeframes, num_contracts))
""" 
print("\nPaste here your Titan Portfolio. Leave a empty line at the end:")
while True:
    line = input()
    if line == '':
        break
    parts = line.split('\t')
    if len(parts) == 3:
        symbol = parts[1][:2]
        strategy_name = parts[1][3:]
        timeframes =  strategy_name.split('_')[4:6]
        num_contracts = parts[2].split('(')[0].strip()
    charts_defn.append(Chart(symbol, strategy_name, timeframes, num_contracts))
 """
print('Got these chart definitions:')
for chart_def in charts_defn:
  print(chart_def)

num_charts_per_workspace = 4
mc = Multicharts(multicharts_path=r'C:/Multicharts.15r6/MultiCharts64.exe')
for idx, chart_def in enumerate(charts_defn):
  if idx%num_charts_per_workspace == 0:
    mc.open_new_workspace()
  mc.new_chart(data_source='TradeStation', instrument=chart_def.symbol, timeframes=chart_def.timeframes, tf_unit='Minute', days_back='90')
  mc.insert_signal(chart_def.strategy_name, num_contracts=chart_def.num_contracts)
  print('Done!')
  time.sleep(3)


#mc.print_control_ids()
