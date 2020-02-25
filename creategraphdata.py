#!/usr/bin/env python
# coding: utf-8

# In[1]:


import json,os


# ### Try to open JSON from ./data folder

# In[2]:


kaartenjson = './data/kaarten.json'
timelinejson = './data/timeline.json'
def createfolders():
    try:
        temp = os.stat('./data')
    except:
        os.mkdir('./data')
if os.path.exists(kaartenjson):
    with open(kaartenjson) as json_file:
        kaarten = json.load(json_file)
else:
    exec(open("./savetrellotojson.py").read())
    with open(kaartenjson) as json_file:
        kaarten = json.load(json_file)
    with open(timelinejson) as json_file:
        timeline = json.load(json_file)


# In[3]:


# Check if data is no more than 1 day old and update if necessary
from datetime import date,datetime,timedelta
with open('./data/date.txt', 'r') as f2:
    date = datetime.strptime(f2.read(),'%Y-%m-%d, %H:%M:%S')

if date < datetime.now() - timedelta(days = 1):
    exec(open("./savetrellotojson.py").read())
    with open(kaartenjson) as json_file:
        kaarten = json.load(json_file)
    with open(timelinejson) as json_file:
        timeline = json.load(json_file)    

