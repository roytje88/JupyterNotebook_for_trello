#!/usr/bin/env python
# coding: utf-8

# In[27]:


exec(open("./variables.py").read())


# In[28]:


cards = json.loads(json.dumps(requests.get(url_cards).json()))
lists = json.loads(json.dumps(requests.get(url_lists).json()))
customfields = json.loads(json.dumps(requests.get(url_customfields).json()))
labels = json.loads(json.dumps(requests.get(url_labels).json()))
members = json.loads(json.dumps(requests.get(url_members).json()))


# In[29]:


customfields_dict = {}
for i in customfields:
    customfields_dict[i['id']] = {}
    if i['type'] == 'date':
        customfields_dict[i['id']][i['name']] = {}
        customfields_dict[i['id']][i['name']]['options'] = {'id': 'date'}
       

    else:
        customfields_dict[i['id']][i['name']] = {}
        customfields_dict[i['id']][i['name']]['options'] = {}
        for j in i['options']:
            customfields_dict[i['id']][i['name']]['options'][j['id']] =  j['value']['text']

customfieldsmetdate = []
for i,j in customfields_dict.items():
        for k,l in j.items():
            try:
                if l['options']['id'] == 'date':
                    customfieldsmetdate.append(i)
            except:
                pass


# In[32]:


kaarten = {}

for i in cards:
        kaarten[i['id']] = {'name': i['name'],
                            'id': i['id'],
                            'idlist': i['idList'],
                            'customfields': i['customFieldItems'],
                            'customfieldvalues': {},
                            'labels': {},
                            'members': {},
                            'sjabloon': i['isTemplate'],
                            'vervaldatum': None

                           }
        
for i,j in kaarten.items():
    date = idtodate(i)
    j['datum aanmaak'] = str(date)
    for k in lists:
        if j['idlist'] == k['id']: j['list'] = k['name'] 
if customfields_dict == {}:
    for i,j in kaarten.items():
        j['customfieldvalues'] = {}
else:

    for i,j in kaarten.items():
        for k in j['customfields']:
        
            for l,m in customfields_dict.items():

                for n,o in m.items():
                    if k['idCustomField'] not in customfieldsmetdate:
                        for p,q in o.items():
                            for r,s in q.items():
                                if r == k['idValue']:
                                    j['customfieldvalues'][n] = s
                    if k['idCustomField'] in customfieldsmetdate:              ## this is a temp solution to hardcode the custom field with type Date.
                        j['customfieldvalues']['Beginnen'] = k['value']['date'][0:10]

                        

                  
for i in cards:
    if i['due'] != None:
        kaarten[i['id']]['vervaldatum'] = i['due'][0:10]
    for j in i['labels']:
        kaarten[i['id']]['labels'][j['name']] = j['id']


for i in cards:
    for j in i['idMembers']:

        for k in members:

            if j == k['id']:
                    kaarten[i['id']]['members'][k['id']] = k['fullName']

for i,j in kaarten.items():
    if j['list'] in lijstenbeginnen:
        j['status'] = 'Niet gestart'
    elif j['list'] in lijstendoing:
        j['status'] = 'Doing'
    elif j['list'] in lijstenblocked:
        j['status'] = 'Blocked'
    elif j['list'] in lijstendone:
        j['status'] = 'Done'

for i,j in kaarten.items():
    del j['customfields']
    del j['idlist']
    del j['id']

tedeletenlijsten = []

for i in lists:
    if i['name'] not in lijstenforscrum:
        tedeletenlijsten.append(i['name'])
tedeletenkaarten = []
for i,j in kaarten.items():
    if j['sjabloon'] == True:
        tedeletenkaarten.append(i)
    elif j['list'] in tedeletenlijsten:
        tedeletenkaarten.append(i)

for i in tedeletenkaarten:
    if i in kaarten:
        del kaarten[i]


# In[33]:


nietgestart = {}
blocked = {}
doing = {}
done = {}

for i,j in kaarten.items():
    if j['list'] in lijstenbeginnen:
        nietgestart[i] = j
    elif j['list'] in lijstenblocked:
        blocked[i] = j
    elif j['list'] in lijstendoing:
        doing[i] = j
    elif j['list'] in lijstendone:
        done[i] = j

