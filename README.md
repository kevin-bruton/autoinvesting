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

