
import json
from runpy import _ModifiedArgv0
from time import sleep
from threading import Thread
from os.path import join, exists
from traceback import print_exc
from random import random
from datetime import datetime, timedelta

from connector import mt_connector_client
from db import save_demo_trade

class read_and_save_trades():

    def __init__(self, MT4_directory_path, 
                 sleep_delay=0.005,             # 5 ms for time.sleep()
                 max_retry_command_seconds=10,  # retry to send the commend for 10 seconds if not successful. 
                 verbose=False
                 ):

        # if true, it will randomly try to open and close orders every few seconds. 
        self.open_test_trades = False

        self.last_open_time = datetime.utcnow()
        self.last_modification_time = datetime.utcnow()

        self.connector = mt_connector_client(self, MT4_directory_path, sleep_delay, 
                              max_retry_command_seconds, verbose=verbose)
        sleep(1)

        self.connector.start()
        
        # account information is stored in self.connector.account_info.
        print("Account info:", self.connector.account_info)


    # triggers when an order is added or removed, not when only modified. 
    def on_order_event(self, event, order, modified_fields=None):
        print(' ***** RECEIVED AN ORDER EVENT ***** ')
        print('       Event: ', event, '')
        print('       Order: ', order)
        if event == 'Order modified':
            print('       Modified fields: ', modified_fields)
        save_demo_trade('Some Strategy name', 'hi')
        
        #print(f'on_order_event. open_orders: {len(self.connector.open_orders)} open orders')



MT4_files_dir = '/Users/kevin/Library/Application Support/MetaTrader 4/Bottles/metatrader64/drive_c/Program Files (x86)/MetaTrader 4/MQL4/Files/'

processor = read_and_save_trades(MT4_files_dir)

while processor.connector.ACTIVE:
    sleep(1)

