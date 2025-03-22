
from dotenv import load_dotenv
from scripts.insert_trades_from_csvs import insert_trades_from_csvs
from scripts.all_trades_to_file_backup import save_all_trades_to_file

load_dotenv()
import sys
import platform
from scripts.update_from_mt import run_update_from_mt
from scripts.update_from_ib import update_from_ib
from scripts.cron import run_cron
from fast.api_server import run_api_server
from scripts.import_strategies import import_strategies
from scripts.update_from_ib import update_from_ib
from scripts.encrypt_text import do_decrypt, do_encrypt
from scripts.create_templates import create_mt_templates
from mc.log_analysis.read_logs import process_last_logentries as update_from_mc
from mc.automation.titan_workspaces import create_mc_workspaces

if platform.system() == 'Windows':
    from scripts.wifi_connector import check_connection

def update_app ():
    import os
    print('\nSTEP 1. UPDATE AUTOINVESTING (git pull)...')
    os.system('git pull')
    os.chdir('../autoinvesting-ui')
    print('\nSTEP 2. UPDATE AUTOINVESTING-UI (git pull)...')
    os.system('git pull')
    print('\nSTEP 3. BUILD AUTOINVESTING-UI (npm run build)...')
    os.system('npm run build')
    os.chdir('../autoinvesting')
    print('\nDONE UPDATING AUTOINVESTING AND AUTOINVESTING-UI!!!\n')

if __name__ == '__main__':
    cmds = {
        'app': run_api_server, # optional second arg: dev or prod
        'update_app': update_app,
        'cron': run_cron if platform.system() == 'Windows' else lambda: print('winwifi not supported on this platform'),
        'update_from_mt': run_update_from_mt,
        'update_from_ib': update_from_ib,
        'update_from_mc': update_from_mc,
        'create_mt_templates': create_mt_templates,
        'create_mc_workspaces': create_mc_workspaces,
        'import_strategies': import_strategies,
        'encrypt': do_encrypt,
        'decrypt': do_decrypt,
        'wifi_connection': check_connection if platform.system() == 'Windows' else lambda: print('winwifi connection not supported on this platform'),
        'save_all_trades_to_file': save_all_trades_to_file,
        'insert_trades_from_csvs': insert_trades_from_csvs
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

    cmds[cmd](*sys.argv[2:])
