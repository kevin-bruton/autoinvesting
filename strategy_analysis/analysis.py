#%%
import os
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import pandas as pd

strategy_dir = '/home/kevin.bruton/.wine/drive_c/sqx137_4/user/projects/EURUSD - H1 Simple/databanks/Results/'

strategy_files = [f for f in os.listdir(strategy_dir) if os.path.isfile(strategy_dir + f)]

def put_values_in_range_and_plot_bar_chart(values, block_width):
  max_value = max(values)
  range_frequencies = {}
  for start_value in range(int(max_value / block_width) + 1):
     range_frequencies[start_value * block_width] = 0
  
  for value in values:
    range_start = int(value / block_width) * block_width
    range_frequencies[range_start] += 1

  df = pd.DataFrame(range_frequencies.items(), columns=['Range', 'Count']).sort_values('Range')
  df.plot.bar(x="Range", y="Count")
  plt.show()

# This analyses the building blocks used in all strategies
# and shows the ones that have been used more times than the threshold defined
def indicator_analysis (threshold=10):
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
    if indicators[indicator]['count'] >= threshold:
      num_selected += 1
      print(indicator, indicators[indicator])

  print('\nNum selected:', num_selected)

def get_node_from_strategy_files (xpath_to_node, action):
  for strategy_file in strategy_files:
    with ZipFile(strategy_dir + strategy_file, 'r') as zipfile:
      with zipfile.open('strategy_Portfolio.xml') as xmlfile:
        root = ET.fromstring(xmlfile.read())
        node = root.find(xpath_to_node)
        action(node)

def sl_fixed_size_analysis(direction='Long'):
  sl = []
  action = lambda node: sl.append(float(node.text))
  xpath = f'.//Rule[@name="{direction} entry"]//Param[@key="#StopLoss.StopLoss#"]//Param'
  get_node_from_strategy_files(xpath, action)
  put_values_in_range_and_plot_bar_chart(values=sl, block_width=5)

def sl_percentage_based_analysis(direction='Long'):
  sl = []
  action = lambda node: sl.append(float(node.text))
  xpath = f'.//Rule[@name="{direction} entry"]//Param[@key="#StopLoss.StopLoss#"]//Param'
  get_node_from_strategy_files(xpath, action)
  put_values_in_range_and_plot_bar_chart(values=sl, block_width=10)

def sl_atr_based_analysis(direction='Long'):
  sl = []
  action = lambda node: sl.append(float(node.text))
  xpath = f'.//Rule[@name="{direction} entry"]//Param[@key="#StopLoss.StopLoss#"]//Param[@key="#Value#"]'
  get_node_from_strategy_files(xpath, action)
  put_values_in_range_and_plot_bar_chart(values=sl, block_width=25)

def tp_atr_based_analysis(direction='Long'):
  sl = []
  action = lambda node: sl.append(float(node.text))
  xpath = f'.//Rule[@name="{direction} entry"]//Param[@key="#ProfitTarget.ProfitTarget#"]//Param[@key="#Value#"]'
  get_node_from_strategy_files(xpath, action)
  put_values_in_range_and_plot_bar_chart(values=sl, block_width=25)

# indicator_analysis()
# sl_fixed_size_analysis()
# sl_percentage_based_analysis()
# sl_atr_based_analysis()
tp_atr_based_analysis()
