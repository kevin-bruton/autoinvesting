# Auto Investing

Strategy performance tracking and investing

## Setup Platform
Environment variables must be set in the `.env` file for the corresponding with the corresponding FLASK_APP='back/api.py', MT_DEMO_FILES_DIR, etc.

Create an autoinvesting MySQL database, adding it's name and credentials to the `.env` file.

Add a user to the Users table of type admin in order to upload the database data.

Upload a previously saved JSON data file.

## Setup Trade Copier
Include the investor users in the Users table.

Include the investor's subscriptions in the subscriptions table.

Make sure that the EA `FileConnector` is installed in the Master MT4 account, and that the EA `AutoInvestingEA` is installed in the Copier MT4 account. The copier's EA must have the appropriate key that coincides with the key in the Users table.


## Run dev server
Select the Python virtual environment, eg. `pyenv activate venv-autoinvesting`  
Start the MySQL DB service, ie. `sudo service mysql start`  
Run the Flask dev server: `flask run` (from the root directory)

In the `autoinvesting-ui` project, the frontend dev server must be started also via: `npm start`
For the frontend to work on port 80, permission must be granted, cf. https://www.digitalocean.com/community/tutorials/how-to-use-pm2-to-setup-a-node-js-production-environment-on-an-ubuntu-vps#give-safe-user-permission-to-use-port-80

We can also set up an entry in the local machine's host file so that we can use for example http://autoinvesting.local to access the dev server's web page.

## Run pro server
`waitress-serve api:app`
(from back directory)

## Makefile for deployment
Makefile should be placed in parent directory  
and then can be used to deploy with the commands:  
`make deploy-front`  
`make deploy-back`  
or just  
`make deploy`  
to deploy both back and front.
The waitress service must be previously setup  
This was meant to be run on an Ubuntu server  

## The waitress service
An example waitress.service file is provided which could be used on an Ubuntu server, for example. It should be put in the `/etc/systemd/system` folder

Reference:  
```
admin@vmi760289:/etc/systemd/system$ cat waitress.service
[Unit]
Description=Python Waitress Server

[Service]
WorkingDirectory=/home/admin/autoinvesting/back/
ExecStart=/home/admin/.pyenv/versions/autoinvesting-env/bin/waitress-serve api:app

[Install]
WantedBy=multi-user.target
```


## Apache
An example Apache file is provided (in the docs directory)
It has to be configured to serve the front end  
and back end on the other hand as reverse proxy etc.

## Dependencies

QuantStats  
PyJWT  
mysql-connector-python  
flask_cors  
python-dotenv  
flask  

dropbox

google-api-python-client  
google-auth-httplib2  
google-auth-oauthlib  

## Import Strategies
To import strategies, use the sqcli to extract the trades csv files from the sqx files  
eg. `./sqcli.exe -tools action=orderstocsv file=“G:\path\to\folder_of_sqx_files” output=“G:\path\to\destination_folder_for_csv_files”`  
Then upload via FTP to the `files/sqx`and the `files/trades` directories.
On the server, run the import of strategies & trades script that uses the trades files: `python import_strategies.py`

## Load strategies into MetaTrader
The provided script `create_mt_templates.py` creates MT template files from .mq4 strategy files. The strategy files must use the following naming convention: {symbol}_The script needs the source and destination directories to be set appropriately. Typically the destination directory will be a subdirectory within the MT4 Files directory in the data folder of the MT4 instance where you want to run the strategies. Initially, we are naming that folder `EaTemplates`.

Once those template files have been generated, inside the MT4 program, the `LoadEAs.mq4` script can be used to load all those strategies in MT4. To do so, previously, the only chart open will be the one where the FileConnector is running. The script `CloseAllCharts.mq4` can be used if there are a lot of charts already open. The `LoadEAs.mq4` script read all template files. For each template file, it will open a chart with the corresponding timeframe and load the corresponding EA on to it.