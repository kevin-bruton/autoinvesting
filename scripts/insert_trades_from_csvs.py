import os
import csv
from db.trades import save_trade, trade_exists, Trade

# Directory containing the CSV files
data_dir = './data'

def insert_trades_from_csvs():
  # Process each file in the data directory
  # The filename of each CSV file must contain the strategy ID and strategy run ID, separated by an underscore, eg. '1_1_trades.csv'
  for filename in os.listdir(data_dir):
    if filename.endswith('.csv'):
      strategy_id, strategy_run_id = filename.split('_')[:2]
      if strategy_id == '0': continue
      file_path = os.path.join(data_dir, filename)
      trades_saved = 0
      with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
          order_id = row['orderId']
          trade_details = str(row)
          trade = Trade(**row)
          if not trade_exists(order_id):
            #save_trade()
            print(f"Saved trade: {row}")
            save_trade(trade)
            trades_saved += 1
            print(f"Saved trade: {trade_details}")
      print(f"Saved {trades_saved} trades from {filename}")
