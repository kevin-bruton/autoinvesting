import os
from uvicorn.config import LOGGING_CONFIG
from uvicorn import run

def run_api_server():
  print('Starting API server...')
  LOGGING_CONFIG["formatters"]["default"]["datefmt"] = "%Y-%m-%d %H:%M:%S"
  LOGGING_CONFIG["formatters"]["access"]["datefmt"] = "%Y-%m-%d %H:%M:%S"
  LOGGING_CONFIG["formatters"]["default"]["fmt"] = "%(asctime)s %(levelprefix)s %(message)s"
  LOGGING_CONFIG["formatters"]["access"]["fmt"] = '%(asctime)s %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s'
  run(
      "fast.api_routes:app",
      host="localhost",
      port=8000,
      # ssl_keyfile=os.getenv('SLL_PRIVKEY'),
      # ssl_certfile=os.getenv('SLL_FULLCHAIN'),
    )
