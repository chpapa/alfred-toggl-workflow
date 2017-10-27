import sys
import applescript

from workflow import Workflow, ICON_INFO

def main(wf):
    query = None
    if len(sys.argv) > 1:
        query = sys.argv[1]

    scpt = applescript.AppleScript('''
        tell application "Things3"
            set inboxToDos to to dos of list "Today"
        end tell

        set todoList to {}
        repeat with todo in inboxToDos
            set taskName to name of toDo
            set todoList to todoList & {taskName}
        end repeat
        return todoList
    ''')

    todos = scpt.run()

    entries = wf.filter(query, todos, min_score=20)
    if not entries:
        wf.add_item("No such task", valid=False, icon=ICON_INFO)
        wf.send_feedback()
        return 0

    for entry in entries:
        wf.add_item(title=entry, arg=entry, autocomplete=entry, valid=True)

    wf.send_feedback()

if __name__ == '__main__':
    wf = Workflow()
    wf.run(main)
