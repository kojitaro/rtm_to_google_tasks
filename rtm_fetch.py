#!/usr/bin/env python
"""
Copyright (c) 2011 Kouji Ohura

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
    
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
    
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from rtm import createRTM
#from var_dump import var_dump
import pickle

try:
    import simplejson as json
except ImportError:
    import json

def cds(d):
    if len(d) == 0:
        return ""
    return d[:len(d)-1]+".000Z"


    

def convert_var(task):
    #print var_dump(task)
    v = {
            "title": task.name,
            #"created": task.created,
            "updated": cds(task.modified),
            }

    if hasattr(task.task, "completed") and len(task.task.completed) > 0:
        v["completed"] = cds(task.task.completed)
        v["status"] = "completed"
    else:
        v["status"] = "needsAction"

    if hasattr(task.task, "due") and len(task.task.due)>0:
        v["due"] = cds(task.task.due)

    notes = ""
    if hasattr(task, "notes"):
        if hasattr(task.notes, "note"):
            if hasattr(task.notes.note, "__iter__"):
                for note in task.notes.note:
                    #print var_dump(note)
                    notes = notes + note.modified + "\n" + note.title + "\n"
            else:
                note = task.notes.note
                notes = notes + note.modified + "\n" + note.title + "\n"

        
    v["notes"] = notes

    return v

def loaddata(rtm):
    rspTasks = rtm.tasks.getList()
    #rspTasks = rtm.tasks.getList(filter='dueWithin:"1 week of today"')
    #print var_dump(rspTasks)


    tasks = []
    if hasattr(rspTasks.tasks, "list") and \
       hasattr(rspTasks.tasks.list, "__getitem__"):
        for l in rspTasks.tasks.list:
            if hasattr(l, "taskseries"):
            #if isinstance(l["taskseries"], (list, tuple)):
                for t in l.taskseries:
                    tasks.append(convert_var(t))
            #else:
                #print var_dump(l)
                #tasks.append(l.taskseries.name)
    #print tasks

    
    out = open("rtm.json", "w")
    json.dump(tasks, out)
    out.close()

def main(api_key, secret):
    token = None
    try:
        f = open('rtm.dat')
        token = pickle.load(f)
    except:
        None

    rtm = createRTM(api_key, secret, token)

    if token == None:
        token = rtm.getToken()
        f = open('rtm.dat','w')
        pickle.dump(token,f)

    loaddata(rtm)

if __name__ == '__main__':
    import sys
    try:
        api_key, secret = sys.argv[1:3]
    except ValueError:
        print >>sys.stderr, 'Usage: ./rtm_fetch.py APIKEY SECRET'
    else:
        main(api_key, secret)
