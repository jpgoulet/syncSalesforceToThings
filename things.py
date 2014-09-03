from Foundation import *
from ScriptingBridge import *
import itertools
from settings import settings
from task import Task

things = SBApplication.applicationWithBundleIdentifier_("com.culturedcode.things")
inboxList = things.lists().objectWithName_('Inbox')
todayList = things.lists().objectWithName_('Today')
nextList = things.lists().objectWithName_('Next')
sfArea = things.areas().objectWithName_(settings.area)


def hasTag(todo, tagName):
    """Check if the todo has a specific tag"""
    for tag in todo.tags():
        if tag.name() == tagName:
            return True
            
    return False


def getTasks(tag='salesforce'):
    """Get all the tasks tagged salesforce in the inbox and salesforce area"""
    tasks = [Task(todo=todo) for todo in itertools.chain(inboxList.toDos(), sfArea.toDos())
                if hasTag(todo, tag)]
                                                    
    return tasks


def addTodo(task):
    """Create a new todo in Things"""
    properties = None
    if task.activityDate:
        date = NSDate.dateWithString_(task.activityDate + ' 04:00:00 +0000')
        properties = NSDictionary.dictionaryWithObjectsAndKeys_(task.subject, 'name',
                                                            task.expandedNote, 'notes',
                                                            'salesforce', 'tagNames',
                                                            date, 'dueDate',
                                                            None)
    else:
        properties = NSDictionary.dictionaryWithObjectsAndKeys_(task.subject, 'name',
                                                            task.expandedNote, 'notes',
                                                            'salesforce', 'tagNames',
                                                            None)
    
    
    todo = things.classForScriptingClass_('to do').alloc().initWithProperties_(properties)
    sfArea.toDos().addObject_(todo)
    todo.setStatus_(task.statusId)
    
    
def modifyTodo(todo, task):
    if task.activityDate and task.activityDate != str(todo.dueDate())[:10]:
        date = NSDate.dateWithString_(task.activityDate + ' 04:00:00 +0000')
        todo.setDueDate_(date)
    
    if todo.name() != task.subject:
        todo.setName_(task.subject)

    if todo.status() != task.statusId:
        todo.setStatus_(task.statusId)        

    todo.setNotes_(task.expandedNote)
    
    
def update(task):
    """Change a todo from sync state to synced"""
    task.todo.setTagNames_('salesforce')
    
    modifyTodo(task.todo, task)
    