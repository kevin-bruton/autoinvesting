"""
    This script starts a local server on the port specified on the line
            creds = flow.run_local_server(port=3001)
    It reads from the credentials.json file which should be downloaded from the Google Console
    And writes to a token.json file when authenticated

    It uses this oauth2 process:
    - read from credentials.json file to create the oauth link that should be opened in the browser
    - Google leads the user through the authorization process with consent screes that have been configured etc.
    - The process ends with Google making a GET request to the redirect URI and providing required credentials as parameters
    - With the parameters, the application then saves a token.json file which will hold the info it needs for future requests

    - Roadmap: plan would be to use this to make backups of files and DB data in Google Drive for AutoInvesting

    DEPENDENCIES:
    google-api-python-client
    google-auth-httplib2
    google-auth-oauthlib
"""
from __future__ import print_function

import os.path
from os import getcwd

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = [
    'https://www.googleapis.com/auth/drive.metadata.readonly',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.appdata',
    'https://www.googleapis.com/auth/drive.file'
]


def main():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            filepath = os.path.join(getcwd(), 'credentials.json')
            print('Credentials file:', filepath)
            flow = InstalledAppFlow.from_client_secrets_file(
                filepath, SCOPES)
            print(' **** Initiated flow object ****')
            creds = flow.run_local_server(port=3001)
            print(' **** Got credentials ****')
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('drive', 'v3', credentials=creds)

        # Call the Drive v3 API
        results = service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            print('No files found.')
            return
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    main()
