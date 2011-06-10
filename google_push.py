#!/usr/bin/env python

try:
    import simplejson as json
except ImportError:
    import json

import gflags
import httplib2

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run

FLAGS = gflags.FLAGS
APPLICATION_NAME="rtm_to_google_tasks"
APPLICATION_VERSION="1.0"

def login(client_id, client_secret):
    # Set up a Flow object to be used if we need to authenticate. This
    # sample uses OAuth 2.0, and we set up the OAuth2WebServerFlow with
    # the information it needs to authenticate. Note that it is called
    # the Web Server Flow, but it can also handle the flow for native
    # applications
    # The client_id and client_secret are copied from the API Access tab on
    # the Google APIs Console
    FLOW = OAuth2WebServerFlow(
           client_id=client_id,
           client_secret=client_secret,
           scope='https://www.googleapis.com/auth/tasks',
           user_agent=APPLICATION_NAME+"/"+APPLICATION_VERSION)

    # To disable the local server feature, uncomment the following line:
    # FLAGS.auth_local_webserver = False

    # If the Credentials don't exist or are invalid, run through the native client
    # flow. The Storage object will ensure that if successful the good
    # Credentials will get written back to a file.
    storage = Storage('google_tasks.dat')
    credentials = storage.get()
    if credentials is None or credentials.invalid == True:
           credentials = run(FLOW, storage)

    # Create an httplib2.Http object to handle our HTTP requests and authorize it
    # with our good Credentials.
    http = httplib2.Http()
    http = credentials.authorize(http)

    # Build a service object for interacting with the API. Visit
    # the Google APIs Console
    # to get a developerKey for your own application.
    service = build(serviceName='tasks', version='v1', http=http)
	
    return service

def push_tasks(service):
    f = open("rtm.json", "r")
    rtm_tasks = json.load(f)
    f.close()

    tasks = service.tasks().list(tasklist='@default').execute()

    #for task in tasks['items']:
    #      print task['title']

    #print rtm_tasks
    for task in rtm_tasks:
        t = {
       	    "title": task["title"],
       	    "status": task["status"],
        }
        #print task
        if task.has_key("due") and len(task["due"]) > 0 :
       	    t["due"] = task["due"]
        if task.has_key("notes") and len(task["notes"]) > 0 :
       	    t["notes"] = task["notes"]
        if task.has_key("completed") and len(task["completed"]) > 0 :
    	    t["completed"] = task["completed"]

        #print t
        result = service.tasks().insert(tasklist='@default', body=t).execute()
        #result = service.tasks().insert(tasklist='@default', body=task).execute()
   	#print result

        

def remove_all_tasks(service):
    tasks = service.tasks().list(tasklist='@default').execute()

    for task in tasks['items']:
          task_id = task['id']
          service.tasks().delete(tasklist='@default', task=task_id).execute()


	
def main(client_id, client_secret):
    service = login(client_id, client_secret)
    remove_all_tasks(service)
    push_tasks(service)

if __name__ == '__main__':
    import sys
    try:
        client_id, client_secret = sys.argv[1:3]
    except ValueError:
        print >>sys.stderr, 'Usage: ./google_push.py CLIENT_ID CLIENT_SECRET'
    else:
        main(client_id, client_secret)

