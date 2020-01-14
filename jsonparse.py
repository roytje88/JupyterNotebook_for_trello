#!/usr/bin/env python
# coding: utf-8

# In[1]:


exec(open("./variables.py").read())


# In[2]:


cards = json.loads(json.dumps(requests.get(url_cards).json()))
lists = json.loads(json.dumps(requests.get(url_lists).json()))
customfields = json.loads(json.dumps(requests.get(url_customfields).json()))
labels = json.loads(json.dumps(requests.get(url_labels).json()))
members = json.loads(json.dumps(requests.get(url_members).json()))


# In[3]:


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


# In[4]:


kaarten = {}
for i in cards:
    kaarten[i['id']] = {'name': i['name'],
                        'id': i['id'],
                        'idlist': i['idList'],
                        'customfields': i['customFieldItems'],
                        'labels': {},
                        'members': {},
                        'sjabloon': i['isTemplate'],
                        'due': None,
                        'closed': i['closed'],
			'attachments': {}
                       }
    for j in i['idMembers']:

        for k in members:

            if j == k['id']:
                    kaarten[i['id']]['members'][k['id']] = k['fullName']
    if i['due'] != None:
        kaarten[i['id']]['due'] = datetime.strptime(i['due'][0:19],'%Y-%m-%dT%H:%M:%S')
    for j in i['labels']:
        kaarten[i['id']]['labels'][j['name']] = j['id']
    for j in i['attachments']:
        try:
            if j['url'][0:21]== 'https://trello.com/c/':
                kaarten[i['id']]['attachments'][j['url'][21:29]] = None
        except:
            pass
                    
if customfields_dict != {}:
    for i,j in customfields_dict.items():
        for k,l in j.items():
            for m,n in kaarten.items():
                n[k] = None

    for i,j in kaarten.items():
        for k in j['customfields']:
            if k['idCustomField'] in customfieldsmetdate:
                for l,m in customfields_dict.items():
                    for n,o in m.items():
                        if k['idCustomField'] == l:
                            j[n] = datetime.strptime(k['value']['date'][0:19],'%Y-%m-%dT%H:%M:%S')
            else:
                for l,m in customfields_dict.items():
                    for n,o in m.items():
                        if k['idCustomField'] == l:
                            for p,q in o.items():
                                for r,s in q.items():
                                    if k['idValue'] == r:
                                        j[n] = s     

for i,j in kaarten.items():
    date = idtodate(i)
    j['created'] = date
    for k in lists:
        if j['idlist'] == k['id']: j['list'] = k['name'] 
    if j['list'] in lijstenbeginnen:
        j['status'] = 'Niet gestart'
    elif j['list'] in lijstendoing:
        j['status'] = 'Doing'
    elif j['list'] in lijstenblocked:
        j['status'] = 'Blocked'
    elif j['list'] in lijstendone:
        j['status'] = 'Done'
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

