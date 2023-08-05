#%%
import os
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import pandas as pd

strategy_dir = '/home/kevin.bruton/.wine/drive_c/sqx/user/projects/EURUSD - H1 Simple/databanks/Results/'

strategy_files = [f for f in os.listdir(strategy_dir) if os.path.isfile(strategy_dir + f)]

def indicator_analysis ():
  indicators = {}
  for strategy_file in strategy_files:
      with ZipFile(strategy_dir + strategy_file, 'r') as zipfile:
          with zipfile.open('strategy_Portfolio.xml') as xmlfile:
              root = ET.fromstring(xmlfile.read())
              items = root.findall('.//signals//Item')
              for item in items:
                  indicator = item.attrib['key']
                  if indicator == 'Boolean' or 'name' not in item.attrib or 'categoryType' not in item.attrib:
                      continue
                  if indicator in indicators:
                      indicators[indicator]['count'] += 1
                  else:
                      indicators[indicator] = {
                          'count': 1,
                          'type': item.attrib['categoryType'],
                          'description': item.attrib['name'] if 'name' in item.attrib else ''
                        }

  print('\nHIGH FREQUENCY INDICATORS:\n')
  num_selected = 0
  for indicator in indicators.keys():
    if indicators[indicator]['count'] >= 10:
      num_selected += 1
      print(indicator, indicators[indicator])

  print('\nNum selected:', num_selected)

def sl_fixed_size_analysis(direction='Long'):
  sl = []
  for strategy_file in strategy_files:
    with ZipFile(strategy_dir + strategy_file, 'r') as zipfile:
      with zipfile.open('strategy_Portfolio.xml') as xmlfile:
        root = ET.fromstring(xmlfile.read())
        sl_value = root.find(f'.//Rule[@name="{direction} entry"]//Param[@key="#StopLoss.StopLoss#"]//Param').text
        sl.append(float(sl_value))

  # Get max value & setup range_frequencies
  max_sl = max(sl)
  block_width = 5
  range_frequencies = {}
  for start_sl in range(int(max_sl / 5) + 1):
     range_frequencies[start_sl * block_width] = 0
  
  for sl_value in sl:
    range_start = int(sl_value / block_width) * block_width
    range_frequencies[range_start] += 1

  df = pd.DataFrame(range_frequencies.items(), columns=['Range', 'Count']).sort_values('Range')
  df.plot.bar(x="Range", y="Count")
  plt.show()

sl_fixed_size_analysis()
