#!/usr/bin/env python
# coding: utf-8

# In[ ]:


exec(open("./cardsperdate.py").read())


# In[ ]:


trellobijlagen = {}
x = 0
for i in cards:
    for j in i['attachments']:
        try:
            if j['url'][0:21]== 'https://trello.com/c/':
                shorturl = j['url'][21:29]
                jsonurl = (j['url'][0:29] + ".json?"+keys)
                trellobijlagen[x] = json.loads(json.dumps(requests.get(jsonurl).json()))
                x += 1
                    
        except:
            pass
        


# In[ ]:


for i,j in kaarten.items():
    if j['attachments'] != {}:
        j['trelloattachments'] = {}
        for k in j['attachments']:
            for l,m in trellobijlagen.items():
                for n,o in m.items():
                    if n == 'shortLink':
                        if k == o:
                            j['trelloattachments'][m['id']] = {'name': m['name']}
    else:
        j['trelloattachments'] = None
        
        

