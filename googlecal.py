from __future__ import print_function
import urlparse
import webbrowser
import BaseHTTPServer
import json
import sys
import random
import datetime
import httplib2

from workflow import Workflow, ICON_INFO
from apiclient import discovery
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.contrib.keyring_storage import Storage


SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_ID = \
    '32073141474-eobhusq49kiumme0rf2bn9386d0grmsq.apps.googleusercontent.com'
CLIENT_SECRET = '7u9MmKu37g2qbusjfT-wVReT'
AUTH_RETURNED = False

def get_credentials():
    store = Storage("com.oursky.ben.toggl", "Google Calendar")
    credentials = store.get()
    if not credentials or credentials.invalid:
        port = random.randint(2000, 8000)

        class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
            def do_GET(s):
                s.send_response(200)
                s.send_header("Content-type", "text/html")
                s.end_headers()
                try:
                    code = urlparse.parse_qs(urlparse.urlparse(s.path).query)["code"][0]
                    credentials = flow.step2_exchange(code)
                    store.put(credentials)
                    s.wfile.write("Done with Toggl Alfred Workflow Auth")
                except Exception as e:
                    s.wfile.write("Something wrong: " + e.message)
                global AUTH_RETURNED
                AUTH_RETURNED = True
        httpd = BaseHTTPServer.HTTPServer(("127.0.0.1", port), Handler)
        flow = OAuth2WebServerFlow(client_id=CLIENT_ID,
                                   client_secret=CLIENT_SECRET,
                                   scope=SCOPES,
                                   redirect_uri="http://127.0.0.1:"+str(port))
        auth_uri = flow.step1_get_authorize_url()
        webbrowser.open_new(auth_uri)
        while not AUTH_RETURNED:
            httpd.handle_request()
    return credentials


def main(wf):
    query = None
    if len(sys.argv) > 1:
        query = sys.argv[1]

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time

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

    alfredObj = []
    if events:
        for event in events:
            if query != None and not event['summary'].startswith(query):
                continue
            start = event['start'].get('dateTime', event['start'].get('date'))
            start = datetime.datetime.strptime(start.split('+')[0], '%Y-%m-%dT%H:%M:%S')
            start = start.strftime('%I:%M')
            alfredObj.append(
                {
                    "title": start + " - " + event['summary'],
                    "arg": event['summary'],
                }
            )

    entries = wf.filter(query, alfredObj, lambda x:x["arg"])

    if not entries:
        wf.add_item("No such task", valid=False, icon=ICON_INFO)
        wf.send_feedback()
        return 0

    for entry in entries:
        wf.add_item(title=entry["title"], arg=entry["arg"], autocomplete=entry["arg"], valid=True)

    wf.send_feedback()

if __name__ == '__main__':
    wf = Workflow()
    wf.run(main)
