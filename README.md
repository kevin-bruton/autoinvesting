# Auto Investing

Strategy performance tracking and investing

## Setup Platform
Environment variables must be set in the `.env` file for the corresponding with the corresponding FLASK_APP='back/api.py', MT_FILES_DIR, etc.

Create an autoinvesting MySQL database, adding it's name and credentials to the `.env` file.

Add a user to the Users table of type admin in order to upload the database data.

Upload a previously saved JSON data file.

## Setup Trade Copier
Include the investor users in the Users table.

Include the investor's subscriptions in the subscriptions table.

Make sure that the EA `FileConnector` is installed in the Master MT4 account, and that the EA `AutoInvestingEA` is installed in the Copier MT4 account. The copier's EA must have the appropriate key that coincides with the key in the Users table.


## Run dev server
`flask run`
(from root directory)

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

## Apache
An example Apache file is provided  
It has to be confiured to serve the front end  
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
