import os
from uvicorn.config import LOGGING_CONFIG
from uvicorn import run
import webbrowser
import threading
from time import sleep

def run_api_server(mode='dev'):
  print('Starting API server...')
  LOGGING_CONFIG["formatters"]["default"]["datefmt"] = "%Y-%m-%d %H:%M:%S"
  LOGGING_CONFIG["formatters"]["access"]["datefmt"] = "%Y-%m-%d %H:%M:%S"
  LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s %(levelprefix)s %(message)s"
  LOGGING_CONFIG["formatters"]["access"]["fmt"] = '%(asctime)s %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'
  if mode == 'dev':
    host = 'localhost' # "autoinvesting.local"
    port = 8000
    #def open_browser():
    #  print('Browser thread waiting for api server...')
    #  sleep(15)
    #  print('Opening browser...')
    #  webbrowser.open('http://localhost:8000')
    #threading.Thread(target=open_browser).start()
    print('Api server starting...')
    run(
        "fast.api_routes:app",
        host=host,
        port=port,
        reload=True,
        log_level="info",
        workers=6
      )
  else:
    run(
        "fast.api_routes:app",
        host="factory.fin-tech.com",
        port=443,
        workers=6,
        ssl_keyfile=os.getenv('SLL_PRIVKEY'),
        ssl_certfile=os.getenv('SLL_FULLCHAIN'),
      )

