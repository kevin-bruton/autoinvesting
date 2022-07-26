# Auto Investing

Strategy performance tracking and investing

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
