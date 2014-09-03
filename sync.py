from settings import settings
import salesforce
import things
from datetime import datetime


if __name__ == '__main__':
    timestamp = datetime.utcnow()
    
    # connect to Salesforce and get all the tasks modified since the last time
    sfTasks = salesforce.getTasks()
    
    # Get all Salesforce tagged tasks from Cultured Code Things 
    thingsTasks = things.getTasks()
    
    # Add or modify all the Salesforce tasks to Things
    for task in sfTasks:
        if task in thingsTasks:
            # modify it
            thingsTask = thingsTasks[thingsTasks.index(task)]
            if thingsTask.lastModifiedDate < task.lastModifiedDate:
                print 'modifying from Salesforce: ' + task.subject
                thingsTask.modified = True
                things.modifyTodo(thingsTask.todo, task)
            
        else:
            # Create a new todo in things (only if not completed)
            if task.statusSf != 'Completed':
                print 'creating from Salesforce: ' + task.subject
                things.addTodo(task)
            
    # Update Salesforce tasks with things tasks that have not been modified but were in Things
    # We only update due date and status
    for task in thingsTasks:
        if not task.modified and task.lastModifiedDate >= settings.lastTimestamp:
            print 'modifying from things: ' + task.subject
            salesforce.modifyTask(task)
            
    # Get all tasks from Cultured Code Things that require to be synced
    syncTasks = things.getTasks(tag='sync')
    for task in syncTasks:
        print 'syncinc from things: ' + task.subject
        salesforce.createTask(task)
        things.update(task)
            
    settings.lastTimestamp = timestamp
    settings.writeToFile()