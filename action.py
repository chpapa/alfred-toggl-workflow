import sys
import json
import requests

from workflow import Workflow
from workflow import PasswordNotFound


def main(wf):
    try:
        apikey = wf.get_password("toggle API Key")
    except PasswordNotFound:
        print "Run tm setapikey [api key] to set the API key of Toggle"
        sys.exit(0)

    query = sys.argv[1]
    cmd = query.strip().lower()

    tapi = (apikey, 'api_token')
    theader = {"Content-Type": "application/json"}

    if cmd == 'stop':
        r = requests.get('https://www.toggl.com/api/v8/time_entries/current', auth=tapi)
        tid = r.json()["data"]["id"]
        r = requests.put('https://www.toggl.com/api/v8/time_entries/' + str(tid) + '/stop', auth=tapi)
        print "Task Stopped"
    else:
        data = {"time_entry":{"description": query, "created_with":"alfred"}}

        task_project = wf.stored_data('task_project')
        if task_project is not None and \
           query in task_project and \
           task_project[query]['pid'] is not None:
            data["time_entry"]["pid"] = task_project[query]['pid']

        r = requests.post('https://www.toggl.com/api/v8/time_entries/start', auth=tapi,
                          headers=theader, data=json.dumps(data))
        print "Run: " + query

if __name__ == '__main__':
    wf = Workflow()
    wf.run(main)
