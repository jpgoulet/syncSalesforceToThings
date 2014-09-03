from settings import settings
import re
from datetime import datetime

pattern = re.compile(r'(?P<description>.*?)\n\nid: (?P<id>.*?)\n.*', flags=re.DOTALL|re.MULTILINE)


# Seems like the Python scripting bridge does not support enum
# as they are non-introspectable types. We need to hardcode them
# See: https://developer.apple.com/library/Mac/DOCUMENTATION/Cocoa/Conceptual/ScriptingBridgeConcepts/AboutScriptingBridge/AboutScriptingBridge.html
status = {'Open': 1952737647, 'Completed': 1952736109, 'Cancelled': 1952736108}


def getStatusString(id):
    """Return the equivalent string"""
    for key, value in status.iteritems():
        if value == id:
            return key
    
    return ''


class Task(object):
    """Represent a task"""
    def __init__(self, todo=None, record=None):
        super(Task, self).__init__()
        
        self.id = ''
        self.subject = ''
        self.description = ''
        self.status = ''
        self.activityDate = ''
        self.lastModifiedDate = ''
        self.ownerName = ''
        self.whoName = ''
        self.whoId = None
        self.whatName = ''
        self.whatId = None
        self.todo = None
        self.modified = False

        if record:
            self.initWithRecord(record)
            
        if todo:
            self.initWithTodo(todo)
        
        
    def initWithRecord(self, record):
        """init from a Salesforce Record"""
        
        self.id = record['Id']
        self.subject = record['Subject']
        self.description = record['Description']
        self.status = record['Status']
        self.activityDate = record['ActivityDate']
        self.lastModifiedDate =  datetime.strptime(record['LastModifiedDate'][:-5],'%Y-%m-%dT%H:%M:%S.%f')
        self.ownerName = record['Owner']['Name']
        self.whoName = record['Who']['Name'] if record['Who'] else ''
        self.whoId = record['Who']['Id'] if record['Who'] else None
        self.whatName = record['What']['Name'] if record['What'] else ''
        self.whatId = record['What']['Id'] if record['What'] else None
        
        
    def initWithTodo(self, todo):
        """ init from a Things todo"""
        
        m = pattern.match(todo.notes())
        
        if m:
            self.id = m.group('id')
            self.description = m.group('description')
        else:
            print 'Could not match id for: ' + todo.name()
            self.description = todo.notes()
            
        self.subject = todo.name()
        self.status = getStatusString(todo.status())
        self.activityDate = str(todo.dueDate())[:10] if todo.dueDate() else None
        self.lastModifiedDate = datetime.strptime(str(todo.modificationDate())[:-6],'%Y-%m-%d %H:%M:%S')
        self.ownerName = settings.user
        
        #keep a copy
        self.todo = todo
        
    
    @property
    def expandedNote(self):
        """return the description for a things note field"""
        note = self.description if self.description else ''
        note += '\n\n'
        note += 'id: ' + self.id + '\n'
        
        note += 'url: [url=' + settings.url + self.id + '] salesforce [/url]\n'
        if self.whoId:
            note += 'who: ' + self.whoName + '\n'
        if self.whatId:
            note += 'what: ' + self.whatName + '\n'
        
        return note
        
        
    @property
    def statusId(self):
        """return the status in int (see note about scripting bridge enum)"""
        if self.status in status:
            return status[self.status]
                
        if self.status == 'Not Started':
            return status['Open']
            
        if self.status == 'In Progress':
            return status['Open']
            
            
        if self.status == 'Deferred':
            return status['Canceled']
        
        #open
        return status['Open']
        
        
    @property
    def statusSf(self):
        """return the status for Salesforce"""
        status = self.status
                        
        if status in ['Not Started', 'In Progress', 'Deferred', 'Completed']:
            pass
                    
        elif status == 'Canceled':
            status = 'Deferred'
            
        elif status == 'Open':
            status = 'In Progress'
        
        return status
        
        
    def __str__(self):
        
        task = 'Id: ' + self.id + '\n'
        task += 'Subject: ' + self.subject + '\n'
        #if self.description:
        #    task += 'Description: ' + self.description + '\n'
        task += 'Status: ' + self.status + '\n'
        task += 'ActivityDate: ' + self.activityDate + '\n'
        task += 'LastModifiedDate: ' + self.lastModifiedDate + '\n'
        task += 'Owner.Name: ' + self.ownerName + '\n'
        if self.whoId:
            task += 'Who.Id: ' + self.whoId + '\n'
            task += 'Who.Name: ' + self.whoName + '\n'
        if self.whatId:
            task += 'What.Id: ' + self.whatId + '\n'
            task += 'What.Name: ' + self.whatName + '\n'
            
        return task.encode('ascii', 'ignore')
        
        
    def __eq__(self, y):
            return self.id == y.id
        