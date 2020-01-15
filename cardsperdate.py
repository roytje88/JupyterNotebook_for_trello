#!/usr/bin/env python
# coding: utf-8

# In[ ]:


exec(open("./jsonparse.py").read())


# In[ ]:


def actions_card(idofcard):
    objectname = json.loads(json.dumps(requests.get(trello_base_url+"cards/"+idofcard+"/actions?actions_limit=500&filter=updateCard,createCard,deleteCard&"+keys).json()))
    return objectname


# In[ ]:


for i,j in kaarten.items():
    j['actions'] = actions_card(i)


# In[ ]:


for i,j in kaarten.items():
    j['movements'] = {}
    for k in j['actions']:
        try:
            j['movements'][k['id']] = {'listBefore': k['data']['listBefore'],
                                       'listAfter': k['data']['listAfter'],
                                       'datum': k['date']
                                      }

        except:
            pass


# In[ ]:


for i,j in kaarten.items():
    j['datestarted'] = None
    j['datedone'] = None
    if j['movements'] != {}:
        for k,l in j['movements'].items():
            tmp = []
            tmp2 = []
            if l['listAfter']['name'] in lijstendoing:
                if l['listBefore']['name'] not in lijstendoing:
                    tmp.append(datetime.strptime(l['datum'][0:19],'%Y-%m-%dT%H:%M:%S'))
                    if datetime.strptime(l['datum'][0:19],'%Y-%m-%dT%H:%M:%S') == min(tmp):
                        j['datestarted'] = min(tmp)
            if l['listAfter']['name'] in lijstendone:
                if j['list'] in lijstendone:
                    tmp2.append(datetime.strptime(l['datum'][0:19],'%Y-%m-%dT%H:%M:%S'))
                    if datetime.strptime(l['datum'][0:19],'%Y-%m-%dT%H:%M:%S') == max(tmp2):
                        j['datedone'] = max(tmp2)
for i,j in kaarten.items():
    if j['datestarted'] == None:
        if j['status'] == 'Doing':
            j['datestarted'] = j['created']
        elif j['status'] == 'Done':
            j['datestarted'] = j['created']
for i,j in kaarten.items():
    if j['status'] == 'Done':
        try:
            delta = j['datedone'] - j['datestarted']
            j['leadtime'] = delta.days
        except:
            j['leadtime'] = None
    else: j['leadtime'] = None


# In[ ]:


for i,j in kaarten.items():
    del j['actions']
    del j['movements']


# In[ ]:


datelist = pd.date_range(end = pd.datetime.today(), periods = 200).to_pydatetime().tolist()
datesdict = {}
for i in datelist:
    datesdict[str(i.date())]= {}


# In[ ]:


now = datetime.now().date()
for i,j in datesdict.items():
    datekey = datetime.strptime(i,'%Y-%m-%d').date()
    j['To do'] = 0
    j['Doing'] = 0
    j['Done'] = 0
    for k,l in kaarten.items():
        if l['created'].date() <= datekey <= now:

            j['To do'] +=1

        if l['datestarted'] != None:
            if l['datestarted'].date() <= datekey:
                j['To do'] -=1
                j['Doing'] +=1
        if l['datedone'] != None:
            if l['datedone'].date() <= datekey:
                j['Doing'] -= 1
                j['Done'] += 1


# In[ ]:


in_out = {}
for i in datelist:
    in_out[str(i.date())]= {}
for i,j in in_out.items():
    j['In'] = 0
    j['Out'] = 0
    for k,l in kaarten.items():
        for m,n in l.items():
            x = 0
            y = 0
            if m=='created':
                if i==str(n)[0:10]:
                    x += 1
                    j['In'] += 1
            if m=='datedone':
                if i==str(n)[0:10]:
                    y += 1
                    j['Out'] += 1
for i,j in in_out.items():
    i = datetime.strptime(i,'%Y-%m-%d')


# In[1]:


for i,j in datesdict.items():
    for k,l in in_out.items():
        if i==k:
            j['In'] = l['In']
            j['Out'] = l['Out']

