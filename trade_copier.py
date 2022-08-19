# traded_symbols = ['NDX', 'XAUUSD', 'WS30']
from queue import Queue
from threading import Thread
from dotenv import load_dotenv
from os import getenv
from time import sleep
from trade_server.trade_receiver import run_receiver
from trade_server.trade_publisher import run_publisher

load_dotenv()

trades_queue = Queue()

receiver_thread = Thread(target=run_receiver, args=(trades_queue,))
publisher_thread = Thread(target=run_publisher, args=(trades_queue,))

receiver_thread.start()
publisher_thread.start()

# receiver_thread.join()
# publisher_thread.join()
