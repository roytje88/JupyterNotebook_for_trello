#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import json,os


# ### Try to open JSON from ./data folder

# In[ ]:


kaartenjson = './data/kaarten.json'
timelinejson = './data/timeline.json'
def createfolders():
    try:
        temp = os.stat('./data')
    except:
        os.mkdir('./data')
if os.path.exists(kaartenjson):
    with open(kaartenjson) as json_file:
        cards = json.load(json_file)
else:
    exec(open("./savetrellotojson.py").read())
    with open(kaartenjson) as json_file:
        cards = json.load(json_file)
    with open(timelinejson) as json_file:
        timeline = json.load(json_file)


# ### Check if data is no more than 1 day old and update if necessary

# In[ ]:


from datetime import date,datetime,timedelta
with open('./data/date.txt', 'r') as f2:
    date = datetime.strptime(f2.read(),'%Y-%m-%d, %H:%M:%S')

if date < datetime.now() - timedelta(hours = 1):
    exec(open("./savetrellotojson.py").read())
    with open(kaartenjson) as json_file:
        cards = json.load(json_file)
    with open(timelinejson) as json_file:
        timeline = json.load(json_file)   


# ### Convert JSON datetime to python datetime

# In[ ]:


kaarten = {}
for i,j in cards.items():
    kaarten[i] = {}
    for k,l in j.items():
        try:
            if l[:5] == 'date,':
                kaarten[i][k] = datetime.strptime(l[6:], '%Y-%m-%d, %H:%M:%S')
            else: 
                kaarten[i][k] = l
        except:
            kaarten[i][k] = l


# ### Load every .json file in ./data folder using above function

# In[ ]:


for i in os.listdir('./data'):
    if i[-5:] == '.json':
        with open('./data/'+i) as json_file:
            exec("%s = json.load(json_file)" % (i[:-5]))


# In[ ]:


for i in chosenlists:
    listname = i.replace(" ","_")
    exec("%s = []" % (listname))


# In[ ]:


tmp = []
for i in statuses:
    tmp.append(i[1].replace(' ','_'))
    statussen = list(dict.fromkeys(tmp))
for i in statussen:
    name = 'Status' +i.replace(" ","_")
    exec("%s = []" % (name))


# In[ ]:


x = []
for i,j in timeline.items():
    x.append(i)
    for k,l in j.items():
        if k in chosenlists:
            for m in chosenlists:
                if m == k:
                    exec("%s.append(l)" % (k.replace(" ","_")))
        try:
            if k[:6] == 'Status':
                if k[7:] in dict(statuses).values():
                    variable = k.replace(' ','',1).replace(' ','_')
                    exec("%s.append(l)" % (variable))
        except:
            pass

