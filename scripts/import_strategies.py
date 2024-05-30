import os
from import_strats.import_strategy import import_strategy

# get list of files in Directory
# for each file:
#   get magic, symbol, timeframe, and demo start from file name
#   get random strategy name
#   get backtest trades from file content
#   

def import_strategies():
  trades_dir = './files/trades'

  print('Importing strategies from', trades_dir, ':')
  with os.scandir(trades_dir) as files:
    for file in files:
      filepath = os.path.join(trades_dir, file.name)
      if os.path.isfile(filepath):
        extension = file.name.split('.')[1]
        if extension == 'csv':
          import_strategy(file.name, filepath)
          # print(".", end='', flush=True)
  print('\nDone!')
