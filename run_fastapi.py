from os import path
root_dir = path.abspath(path.dirname(__file__))

from fast.api_server import run_api_server

run_api_server()
