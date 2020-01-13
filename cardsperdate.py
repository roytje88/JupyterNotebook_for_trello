#!/usr/bin/env python
# coding: utf-8

# In[1]:


exec(open("./jsonparse.py").read())


# In[2]:


def actions_card(idofcard):
    objectname = json.loads(json.dumps(requests.get(trello_base_url+"cards/"+idofcard+"/actions?actions_limit=500&filter=updateCard,createCard,deleteCard&"+keys).json()))
    return objectname


# In[3]:


for i,j in kaarten.items():
    j['actions'] = actions_card(i)


# In[4]:


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


# In[12]:


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


# In[14]:


datelist = pd.date_range(end = pd.datetime.today(), periods = 100).to_pydatetime().tolist()
datesdict = {}
for i in datelist:
    datesdict[str(i.date())]= {}


# In[ ]:




