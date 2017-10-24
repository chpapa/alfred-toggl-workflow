import time
import datetime

from workflow import Workflow, PasswordNotFound
import requests

def get_recent_time_entries(api_key):
    url = 'https://www.toggl.com/api/v8/time_entries'
    auth = (api_key, "api_token")
    r = requests.get(url, auth=auth)
    entries = r.json()
    return entries

def main(wf):
    try:
        api_key = wf.get_password('toggle API Key')

        def wrapper():
            return get_recent_time_entries(api_key)

        entries = wf.cached_data('time_entries', wrapper, max_age=600)
        wf.logger.debug('{} Toggl time entries cached'.format(len(entries)))

        data = wf.stored_data('task_project')
        if data is None:
            data = {}

        for entry in entries:
            if 'pid' not in entry:
                entry['pid'] = None

            start = time.mktime(datetime.datetime.strptime(entry['start'][:-6], "%Y-%m-%dT%H:%M:%S").timetuple())
            data[entry['description']] = {'pid': entry['pid'], 'start': start}

        wf.store_data('task_project', data)
    except PasswordNotFound:
        wf.logger.error('No API key saved')

if __name__ == '__main__':
    wf = Workflow()
    wf.run(main)


