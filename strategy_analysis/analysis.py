#%%
import os
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import pandas as pd

strategy_dir = '/home/kevin.bruton/.wine/drive_c/sqx_137/user/projects/EURUSD - H1 Simple/databanks/Results/'

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
                  if indicator == 'Boolean' \
                    or 'name' not in item.attrib \
                    or 'categoryType' not in item.attrib \
                    or item.attrib['categoryType'] == 'operators':
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
  sort_criteria = lambda ind: ind['count']
  ind_list = list(indicators.values())
  ind_list.sort(reverse=True, key=sort_criteria)
  num_selected = 0
  for indicator in ind_list:
    if indicator['count'] >= threshold:
      num_selected += 1
      print(indicator['count'], indicator['description'])

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

def get_nodes_from_strategy_files (xpath_to_node, filter_nodes, action):
  for strategy_file in strategy_files:
    with ZipFile(strategy_dir + strategy_file, 'r') as zipfile:
      with zipfile.open('strategy_Portfolio.xml') as xmlfile:
        root = ET.fromstring(xmlfile.read())
        nodes = root.findall(xpath_to_node)
        filtered_nodes = filter_nodes(nodes)
        action(filtered_nodes)

def edge_detection (threshold_frequency=10):
  indicators = []
  xpath = './/signals//Item'
  def filter_node(nodes):
    filtered_nodes = []
    for node in nodes:
      indicator = node.attrib['key']
      if indicator == 'Boolean' \
        or 'name' not in node.attrib  \
        or 'categoryType' not in node.attrib:
        continue
      filtered_nodes.append(node)
    return filtered_nodes
  action = lambda nodes: indicators.append([n.attrib['name'] for n in nodes])
  get_nodes_from_strategy_files(xpath, filter_node, action)
  indicator_count = {}
  for indicator in indicators:
    if len(indicator):
      indicator_str = ','.join(indicator)
      if indicator_str in indicator_count.keys():
        indicator_count[indicator_str] += 1
      else:
        indicator_count[indicator_str] = 1

  for ind in indicator_count.keys():
    if indicator_count[ind] >= threshold_frequency:
      print(ind, indicator_count[ind])
   

indicator_analysis(threshold=15)
# sl_fixed_size_analysis()
# sl_percentage_based_analysis()
# sl_atr_based_analysis()
# tp_atr_based_analysis()
# edge_detection(threshold_frequency=10)

# %%
