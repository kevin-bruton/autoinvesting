
from dotenv import load_dotenv

load_dotenv()
import sys
from scripts.update_from_mt import run_update_from_mt
from scripts.cron import run_cron
from fast.api_server import run_api_server
from scripts.import_strategies import import_strategies
from scripts.update_from_ib import update_from_ib
from scripts.encrypt_text import do_decrypt, do_encrypt
from scripts.wifi_connector import check_connection
from scripts.create_mt_templates import create_templates

cmds = {
    'api': run_api_server,
    'cron': run_cron,
    'update_from_mt': run_update_from_mt,
    'create_templates': create_templates,
    'import_strategies': import_strategies,
    'update_from_ib': update_from_ib,
    'encrypt': do_encrypt,
    'decrypt': do_decrypt,
    'wifi_connection': check_connection
}

if len(sys.argv) < 2:
    print('Please provide a script name to run')
    print('Usage: run.py <command>')
    print('Available commands:', cmds.keys())
    sys.exit(1)
    
cmd = sys.argv[1]
if cmd not in cmds.keys():
    print('Invalid command. Available commands:', cmds.keys())
    sys.exit(1)

if len(sys.argv) > 2:
    cmds[cmd](sys.argv[2])
else:
    cmds[cmd]()
