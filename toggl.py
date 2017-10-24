import sys

from workflow import Workflow, ICON_INFO
from workflow.background import run_in_background, is_running

def main(wf):
    query = None
    if len(sys.argv) > 1:
        query = sys.argv[1]

    task_project = wf.stored_data('task_project')

    if not wf.cached_data_fresh('time_entries', max_age=600) or task_project is None:
        cmd = ['/usr/bin/python', wf.workflowfile('update_toggl_history.py')]
        run_in_background('update_toggl', cmd)

    if is_running('update'):
        wf.add_item('Getting toggl data',
                    valid=False,
                    icon=ICON_INFO)

    if not query:
        wf.send_feedback()
        return 0

    if task_project:
        tasks = sorted(task_project.keys(), key=lambda x: task_project[x]['start'], reverse=True)
        entries = wf.filter(query, tasks, min_score=30)

        if not entries:
            wf.add_item(query, arg=query, valid=True)
            wf.send_feedback()
            return 0

        for entry in entries:
            wf.add_item(title=entry, arg=entry, autocomplete=entry, valid=True)

    wf.send_feedback()

if __name__ == '__main__':
    wf = Workflow()
    wf.run(main)
