from __future__ import print_function
import httplib2
import os
import json
import sys

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    query = None
    if len(sys.argv) > 1:
        query = sys.argv[1]

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time

    tmpNow = datetime.datetime.utcnow()
    endofday = datetime.datetime(year=tmpNow.year,
                        month=tmpNow.month,
                        day=tmpNow.day,
                        hour=23,
                        minute=59,
                        second=59).isoformat() + 'Z'
    eventsResult = service.events().list(
        calendarId='primary', timeMin=now, timeMax=endofday, maxResults=10, singleEvents=True,
        orderBy='startTime').execute()
    events = eventsResult.get('items', [])

    alfredJSONObj = {"items":[]}
    if events:
        for event in events:
            if query != None and not event['summary'].startswith(query):
                continue
            start = event['start'].get('dateTime', event['start'].get('date'))
            start = datetime.datetime.strptime(start.split('+')[0], '%Y-%m-%dT%H:%M:%S')
            start = start.strftime('%I:%M')
            alfredJSONObj["items"].append(
                {
                    "title": start + " - " + event['summary'],
                    "arg": event['summary'],
                    "autocomplete": event['summary']
                }
            )

    print(json.dumps(alfredJSONObj))

if __name__ == '__main__':
    main()
