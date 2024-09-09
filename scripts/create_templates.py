#
# Prerequisite:
#   - Create a folder called "EaTemplates" in the MQL4/Files folder of the MT4 installation
#   - Have a folder prepared with the .mq4 files
#   - Each mq4 file should be named with the format {symbol}_{timeframe}_{magic}
# 
# This script reads the source directory's contents and uses the .mq4 files found there
# to construct MT4 template files and places them in the destination directory
# The next step would be to run the MT4 script "LoadEas"
# That MT4 script will load the temaplates with the EAs defined there, each on their own chart
# with the appropriate symbol and timeframe, based on the filename of the original mq4 file
# The filename of the mq4 file should be of the format {symbol}_{timeframe}_{magic}
# eg. EURUSD_H1_230601001
#

from enum import Enum
from dotenv import load_dotenv
load_dotenv() 

from os import getcwd, listdir, mkdir, remove, getenv, path
from os.path import isfile, join
from random import randrange
from fast.utils import get_project_root_dir
from db.accounts import get_mt_files_dir, get_mt_instance_dir_name

def create_mt_templates(mt_instance_name):
    """
    Create MT4 templates from the mq4 files in the source directory
    and place them in the account's MT4 instance's EaTemplates folder
    """

    mt_files_dir = getenv('MT_INSTANCES_DIR') + mt_instance_name + '/MQL4/Files/'
    ea_source_dir = path.join(get_project_root_dir(), 'files', mt_instance_name + '_eas_to_install')
    if not mt_files_dir:
        raise Exception('MT directory not found for account {account_id}. Exiting...')
    destination_dir = path.join(mt_files_dir, 'EaTemplates/')
    template = '<chart>\n'
    template2 = """scale=8
graph=1
fore=0
grid=0
volume=0
scroll=1
shift=0
ohlc=1
one_click=0
one_click_btn=1
askline=0
days=0
descriptions=0
shift_size=20
fixed_pos=0
window_left=88
window_top=88
window_right=1531
window_bottom=661
window_type=3
background_color=11119017
foreground_color=0
barup_color=32768
bardown_color=255
bullcandle_color=32768
bearcandle_color=255
chartline_color=0
volumes_color=32768
grid_color=12632256
askline_color=17919
stops_color=17919

<window>
height=100
fixed_height=0
<indicator>
name=main
</indicator>
</window>

<expert>
"""


    # Delete existing files in destination
    if not path.exists(destination_dir):
        mkdir(destination_dir)
        print(f'  Created templates directory for account {mt_instance_name}:', destination_dir)
    files = [f for f in listdir(destination_dir) if '.tpl' in f]
    for filename in files:
        remove(destination_dir + filename)

    onlyfiles = [f for f in listdir(ea_source_dir) if isfile(join(ea_source_dir, f))]
    onlyMt4Files = [f[:-4] for f in onlyfiles if f[-3:] == 'mq4']

    for filename in onlyMt4Files:
        #print(f'Processing {filename}...')
        filename_parts = filename.split('_')
        symbol = filename_parts[0]
        period = filename_parts[1]
        magic = filename_parts[2].split('.')[0]

        # Generate chart ID
        chart_id = ''
        for i in range(18):
            chart_id += str(randrange(10))
        
        template = '<chart>\n'
        template += f'id={chart_id}\n'
        template += f'symbol={symbol}\n'

        # Get period in minutes
        mins = 60
        if period == 'M5': mins = 5
        if period == 'M15': mins = 15
        if period == 'M30': mins = 30
        if period == 'H1': mins = 60
        if period == 'H4': mins = 240
        if period == 'D1': mins = 1440

        template += f'period={mins}\n'

        # Get decimals
        decimals = 5
        symbols_decimals = {
            'EURUSD': 5,
            'XAUUSD': 2,
            'WS30':   0,
            'NDX':    1,
            'AUDUSD': 5
        }
        if not (symbol in symbols_decimals.keys()):
            raise Exception("Error: symbol " + symbol + " decimals not registered in create_templates")
        decimals = symbols_decimals[symbol]

        template += 'leftpos=1296\n'
        template += f'digits={decimals}\n'

        template += template2

        # Get name
        name = f'{symbol}_{period}_{magic}'
        template += f'name={name}\n'

        template += 'flags=279\n'
        template += 'window_num=0\n'
        template += '<inputs>\n'

        # Get inputs
        file1 = open(ea_source_dir + '/' + filename + '.mq4', 'r')
        lines = file1.readlines()
        file1.close()
        for line in lines:
            line_parts = line.split(' ')
            if len(line_parts) and line_parts[0] == 'extern':
                input_name = line_parts[2]
                if line_parts[4][0] == '"':
                    input_value = line_parts[4].split('"')[1]
                else:
                    input_value = line_parts[4].split(';')[0]
                template += f'{input_name}={input_value}\n'
        
        template += '</inputs>\n'
        template += '</expert>\n'
        template += '</chart>\n'

        template_filename = destination_dir + f'{symbol}_{period}_{magic}.tpl'
        template_file = open(template_filename, 'w')
        template_file.write(template)
        template_file.close()
        print(f'  {template_filename} created.')
