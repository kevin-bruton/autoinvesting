from uvicorn import run

def run_api_server():
  print('Starting API server...')
  run("fast.api_routes:app", \
      host="0.0.0.0", \
      port=10443, \
      #ssl_keyfile=get_config_value('ssl_privkey'), \
      #ssl_certfile=get_config_value('ssl_fullchain')
    )
