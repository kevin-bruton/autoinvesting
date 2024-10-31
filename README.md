# Auto Investing

Strategy performance tracking and investing

## Setup Platform
Environment variables must be set in the `.env` file. The `.env.example` file can be used as a reference.

Add a user to the Users table of type admin in order to upload the database data.

Run the production version of the app with `python run.py app`

Select the Python virtual environment, eg. `pipenv shell`

## Setup Account Tracking

Make sure that the EA `FileConnector` is installed in the MT account you want to track.

Run the cron jobs for updating and wifi connection maintenance with `python run.py cron`.

## Run dev server

The VSCode debug launch included in the project can be used for backend development.

In the `autoinvesting-ui` project, the frontend dev server must be started also via: `npm start`
For the frontend to work on port 80, permission must be granted, cf. https://www.digitalocean.com/community/tutorials/how-to-use-pm2-to-setup-a-node-js-production-environment-on-an-ubuntu-vps#give-safe-user-permission-to-use-port-80

We can also set up an entry in the local machine's host file so that we can use for example http://autoinvesting.local to access the dev server's web page.


## Update project

Run `python run.py update_app` to do a git pull on both frontend and backend projects, and to build the frontend.


## Import Strategies

To obtain the csv files of the strategies, the CLI can be used as follows, but at least for the first import all files can be more easily exported from SQX from the GUI:
eg. `./sqcli.exe -tools action=orderstocsv file=“G:\path\to\folder_of_sqx_files” output=“G:\path\to\destination_folder_for_csv_files”`  
Then upload via FTP to the `files/sqx`and the `files/trades` directories.
On the server, run the import of strategies & trades script that uses the trades files: `python import_strategies.py`

More updated instructions on strategy updating and SQX exporting can be found in the AutoInvesting Methodology Google Drive document.
