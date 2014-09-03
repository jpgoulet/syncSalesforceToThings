from simple_salesforce import Salesforce
from settings import settings
from task import Task

sf = Salesforce(username=settings.email, password=settings.password, security_token=settings.token)


def getTasks():
    """Get all the current tasks from salesforce"""
    query = """SELECT   Id,
                        Subject,
                        Description,
                        Status,
                        ActivityDate,
                        LastModifiedDate,
                        Owner.Name,
                        Who.Name,
                        Who.ID,
                        What.Name,
                        What.ID
                FROM Task 
                WHERE Owner.Name = '{user}'
                AND LastModifiedDate > {timestamp}
            """.format(user=settings.user, timestamp=settings.lastTimestamp.isoformat()[:-3] + '+0000')
            
    records = sf.query_all(query)
    tasks = []
    
    for record in records['records']:
        task = Task(record=record)
        tasks.append(task)
        
    return tasks

def modifyTask(task):
    sf.Task.update(task.id, {'ActivityDate': task.activityDate, 'Subject': task.subject, 'Status': task.statusSf, 'Description': task.description})
    
    
def createTask(task):
    state = None
    
    if task.activityDate:
        state = sf.Task.create({'ActivityDate': task.activityDate, 'Subject': task.subject, 'Status': task.statusSf, 'Description': task.description})
    else:
        state = sf.Task.create({'Subject': task.subject, 'Status': task.statusSf, 'Description': task.description})
    
    if state[u'success']:
        task.id = state['id']
        return True
    else:
        print state
        return False