#!/usr/bin/env python
# coding: utf-8

# ## Import libraries

# In[ ]:


import requests,json,os, pprint,requests
import pandas as pd
from datetime import date,datetime,timedelta


# ### Set configuration files variables

# In[ ]:


configurationfile = './configuration/configuration.txt'
credentialsfile = './configuration/credentials.txt'


# ### Create folders if they don't exist

# In[ ]:


def createfolders():
    try:
        temp = os.stat('./configuration')
    except:
        os.mkdir('./configuration')
    try:
        temp = os.stat('./data')
    except:
        os.mkdir('./data')
createfolders()


# ### Open all options

# In[ ]:


with open('credentialsoptions.txt') as json_file:
    credentialsoptions = json.load(json_file)
with open('configoptions.txt') as json_file:
    configoptions = json.load(json_file)


# ### Load configuration and credentials

# In[ ]:


def loadconfig():
    global configfound
    global credentialsfound
    global config
    global credentials
    if os.path.exists(configurationfile):
        with open(configurationfile) as json_file:
            config = json.load(json_file)
        configfound = True
    else:
        config = {}
        for i,j in configoptions.items():
            config[i] = j
            configfound = False

    if os.path.exists(credentialsfile):
        with open(credentialsfile) as json_file:
            credentials = json.load(json_file)
        credentialsfound = True
    else:
        credentials = {}
        for i,j in credentialsoptions.items():
            credentials[i] = j
        credentialsfound=False
loadconfig()


# ### Create function to convert config file

# In[ ]:


def updateconfig(file,olddict,newdict):
    ans = input('Old or no ' + file[16:] + ' found. Update now? (Y/N)')
    if ans.upper() != 'N':
        print('This is your old config:')
        pprint.pprint(olddict)
    newconfig = {}
    newconfig['Version'] = newdict['Version']
    newconfig['__Comment'] = newdict['__Comment']
    keystoupdate = []
    for i,j in olddict.items():
        if type(j) == dict:
            for k,l in j.items():
                if l == True:
                    newconfig[i][k] = True
                else:
                    keystoupdate.append(k)
        elif type(j) == list:
            if j == []:
                keystoupdate.append(i)
            else:
                newconfig[i] = j
        else:
            if j != '':
                newconfig[i] = j
            else:
                keystoupdate.append(i)
    for i,j in newdict.items():
        if type(j) == list:
            if i in keystoupdate:
                newconfig[i] = []
                value = input('Give the number of lists to add for the status '+i)
                if value != '0':
                    try:
                        x = int(value)
                    except:
                        x = int(input('Not an integer. Please try again!'))
                    count = 1
                    while count <= x:
                        newconfig[i].append(input('Give the name of one list each time for the status ' + i))
                        count += 1
        elif type(j) == dict:
            newconfig[i] = {}
            for k,l in j.items():
                if k in keystoupdate:
                    answer = input(k + ' (Y/N)').upper()
                    if answer == 'Y':
                        newconfig[i][k] = True
                    else:
                        newconfig[i][k] = False
        else:
            if i in keystoupdate:
                newconfig[i] = input(i)
    with open(file, 'w') as outfile:
        json.dump(newconfig, outfile, indent=4, sort_keys=True)


# ### Check which version of the configuration is loaded and ask to update it

# In[ ]:


try:
    version = float(config['Version'])
except:
    version = 0.0
if version == 0.0 or version < float(configoptions['Version']) or configfound == False:
    updateconfig(configurationfile, config, configoptions)
    loadconfig()
try:
    version = float(credentials['Version'])
except:
    version = 0.0
if version == 0.0 or version < float(credentialsoptions['Version']) or credentialsfound == False:
    updateconfig(credentialsfile,credentials, credentialsoptions)
    loadconfig()


# ### Create URLs

# In[ ]:


keys = "key="+credentials.get('API key')+"&token="+credentials.get('API token')
trello_base_url = "https://api.trello.com/1/"
board_url = trello_base_url+"boards/"+config.get('Board ID')
url_cards = board_url+"/cards?attachments=true&customFieldItems=true&filter=all&"+keys
url_lists = board_url+"/lists?filter=all&"+keys
url_customfields = board_url+"/customFields?"+keys
url_labels = board_url+"/labels?"+keys
url_members = board_url+"/members?"+keys


# ### Get the JSON objects and parse them

# In[ ]:


cards = json.loads(json.dumps(requests.get(url_cards).json()))
lists = json.loads(json.dumps(requests.get(url_lists).json()))
customfields = json.loads(json.dumps(requests.get(url_customfields).json()))
labels = json.loads(json.dumps(requests.get(url_labels).json()))
members = json.loads(json.dumps(requests.get(url_members).json()))


# ### Create function to convert the JSON Time in string format to DateTime

# In[ ]:


def dateCalc(date):
    newdate = datetime.strptime(date[0:19],'%Y-%m-%dT%H:%M:%S')
    return newdate


# ### Create dictionary for custom fields (if exists)

# In[ ]:


customfields_dict = {'date': {},'list': {}, 'text': {}, 'number': {}, 'checkbox': {}}
for i in customfields:
    customfields_dict[i['type']] = {}
for i in customfields:
    customfields_dict[i['type']][i['id']] = {}
for i in customfields:
    if i['type'] == 'list':
        customfields_dict[i['type']][i['id']]['name'] = i['name']
        customfields_dict['list'][i['id']]['options'] = {}
        for j in i['options']:
            customfields_dict['list'][i['id']]['options'][j['id']] = j['value'].get('text')
    else:
        customfields_dict[i['type']][i['id']]['name'] = i['name']


# ## Create a list for all the chosen lists in the configuration

# In[ ]:


chosenlists = []
for i in config.get('Not Started'):
    chosenlists.append(i)
chosenlists.extend(config.get('Blocked'))
chosenlists.extend(config.get('Doing'))
chosenlists.extend(config.get('Done'))
if config['Script options']['Calculate hours'] == True:
    chosenlists.append('Doorlopend')


# ### Create function to get the hashed date from the card ID

# In[ ]:


def idtodate(cardid):
    hex = cardid[0:8]
    timestamp = int(hex,16)
    timedate = datetime.fromtimestamp(timestamp)
    return timedate


# ### Create dictionary with all cards

# In[ ]:


kaarten = {}
for i in cards:
    kaarten[i['id']] = {'name': i['name'],
                        'cardid': i['id'],
                        'idlist': i['idList'],
                        'customfields': i['customFieldItems'],
                        'labels': {},
                        'members': {},
                        'sjabloon': i['isTemplate'],
                        'due': None,
                        'closed': i['closed'],
                        'attachments': {},
                        'shortUrl': i['shortUrl']
                       }
    for j in i['idMembers']:

        for k in members:

            if j == k['id']:
                    kaarten[i['id']]['members'][k['id']] = k['fullName']
    if i['due'] != None:
        kaarten[i['id']]['due'] = dateCalc(i['due'])
    for j in i['labels']:
        kaarten[i['id']]['labels'][j['id']] = j['name']
    for j in i['attachments']:
        try:
            if j['url'][0:21]== 'https://trello.com/c/':
                kaarten[i['id']]['attachments'][j['url'][21:29]] = None
        except:
            pass


# ### Add custom fields if they exist

# In[ ]:


if customfields_dict != {}:
    for i,j in customfields_dict.items():
        for k,l in j.items():
            for m,n in kaarten.items():
                n[l['name']] = None
    for i,j in kaarten.items():
        for k in j['customfields']:
            if k['idCustomField'] in customfields_dict['list'].keys():
                j[customfields_dict['list'][k['idCustomField']].get('name')] = customfields_dict['list'][k['idCustomField']]['options'].get(k['idValue'])
            elif k['idCustomField'] in customfields_dict['checkbox'].keys():
                if k['value']['checked'] == 'true':
                    j[customfields_dict['checkbox'][k['idCustomField']].get('name')] = True
                else:
                    j[customfields_dict['checkbox'][k['idCustomField']].get('name')] = False
            elif k['idCustomField'] in customfields_dict['date'].keys():
                j[customfields_dict['date'][k['idCustomField']].get('name')] =  dateCalc(k['value'].get('date')) 
            else:
                for key in k['value']:
                    j[customfields_dict[key][k['idCustomField']].get('name')] = k['value'].get(key)


# ### Add the statuses (Not started, Doing, Blocked and Done), based on the configuration

# In[ ]:


for i,j in kaarten.items():
    date = idtodate(i)
    j['created'] = date
    for k in lists:
        if j['idlist'] == k['id']: j['list'] = k['name']
    if j['list'] in config.get('Not Started'):
        j['status'] = 'Not Started'
    elif j['list'] in config.get('Doing'):
        j['status'] = 'Doing'
    elif j['list'] in config.get('Blocked'):
        j['status'] = 'Blocked'
    elif j['list'] in config.get('Done'):
        j['status'] = 'Done'
    elif j['list'] in config.get('Always continuing'):
        j['status'] = 'Always continuing'
    else:
        j['status'] = 'Archived'
    del j['customfields']
    del j['idlist']


# ### Give the status Archived if the card is closed and not done

# In[ ]:


for i,j in kaarten.items():
    if j['closed'] == True and j['status'] != 'Done':
        j['status'] = 'Archived'


# ### Create object with lists that are not chosen

# In[ ]:


liststodelete = []
for i in lists:
    if i['name'] not in chosenlists:
        liststodelete.append(i['name'])


# ### Create object with all cards that should be deleted (ignored)

# In[ ]:


cardstodelete = []
for i,j in kaarten.items():
    if j['sjabloon'] == True:
        cardstodelete.append(i)
    elif j['list'] in liststodelete:
        cardstodelete.append(i)


# ### Before deleting, create a dict for the hours calculation

# In[ ]:


hours = {}
for i,j in kaarten.items():
    if j['list'] == 'Uren':
        hours[j['name']] = {config['Custom Field for Starting date']: j['Begindatum'], config['Custom Field for Ending date']: j['Einddatum'], config['Custom Field with hours per month']: j['Uren per maand']}


# ### Delete the cards in the object 'cardstodelete'

# In[ ]:


for i in cardstodelete:
    if i in kaarten:
        del kaarten[i]


# ### Get all actions from the board (if limit of 1000 exceeds, repeat the API request)

# In[ ]:


actions = []
before = datetime.now().strftime("%Y-%m-%dT%H:%M:%S"+".000Z")
x = 1000
while x == 1000:
    actionsurl = board_url+"/actions?before="+before+"&limit=1000&filter=updateCard&"+keys
    temp = json.loads(json.dumps(requests.get(actionsurl).json()))
    tmp = []
    for i in temp:
        actions.append(i)
        for j,k in i.items():
            if j == 'date':
                tmp.append(k)
    before = min(tmp)
    x = len(temp)


# ### Add the actions to the appropiate card

# In[ ]:


for n,o in kaarten.items():
    o['actions'] = []
    for i in actions:
        for j,k in i.items():
            if j == 'data':
                for l,m in k.items():
                    if l == 'card':
                        if n == m['id']:
                            o['actions'].append(i)


# ### Get all list movements of all cards

# In[ ]:


for i,j in kaarten.items():
    j['listmovements'] = {}
    for k in j['actions']:
        for l,m in k.items():
            try:
                j['listmovements'][dateCalc(k['date'])] = {'listAfter': k['data']['listAfter']['id'], 'listBefore': k['data']['listBefore']['id']}
            except:
                pass


# ### Determine the right list movements with date and time (including the fist list)

# In[ ]:


for i,j in kaarten.items():
    j['movements'] = {}
    if j['listmovements'] == {}:
        j['movements'][j['created']] = {'listBefore': None, 'listAfter': j['list']}
    else:
        tmpdates = []
        for k,l in j['listmovements'].items():
            tmpdates.append(k)
        for m in tmpdates:
            for n,o in j['listmovements'].items():
                if n == m:
                    j['movements'][m] = {'listAfter': o['listAfter'],'listBefore': o['listBefore']}
        for k,l in j['listmovements'].items():
            if k == min(tmpdates):
                j['movements'][j['created']] = {'listBefore': None, 'listAfter': l['listBefore']}

for i,j in kaarten.items():
    del j['actions']


# ### Because listnames could be changed, the list ID was added in previous commands. With this code, the current listname is displayed

# In[ ]:


historicallists = []
historicallists.extend(chosenlists)

for i,j in kaarten.items():
    for k,l in j['movements'].items():
        for m,n in l.items():
            for o in lists:
                if o['id'] == n:
                    l[m] = o['name']
                    historicallists.append(o['name'])


# ### Create a dictionary with date-keys (past 400 days)

# In[ ]:


datesdict = {}
now = datetime.now().date()
numdays = 365

for x in range (0, numdays):
    datesdict[str(now - timedelta(days = x))] = {}
    datesdict[str(now + timedelta(days = x))] = {}


# ### Create a list for the categories

# In[ ]:


if config['Script options'].get('Calculate hours') == True:
    categories = []
    for i,j in customfields_dict['list'].items():
        if j['name'] == config['Custom Field for Categories']:
            for k in j['options'].values():
                categories.append(k)


# ### Determine how many cards were in what list on the dates in the Dates-dictionary

# In[ ]:


for i,j in datesdict.items():
    datekey = datetime.strptime(i,'%Y-%m-%d').date()
    for k in historicallists:
        j[k] = 0
    for l,m in kaarten.items():
        if m['list'] in chosenlists:
            if m['status'] != 'Archived':
                for n,o in m['movements'].items():
                    if n.date() <= datekey <= now:
                        if o['listBefore'] != None:
                            j[o['listBefore']] -= 1
                            j[o['listAfter']] += 1
                        else:
                            j[o['listAfter']] += 1


# ### Do the same for categories (if option is enabled)

# In[ ]:


if config['Script options'].get('Calculate hours') == True:
    for i,j in datesdict.items():
        datekey = datetime.strptime(i,'%Y-%m-%d').date()
        for k,l in hours.items():
            name = 'Hours ' + k
            j[name] = 0
            if l[config['Custom Field for Starting date']].date() <= datekey <= l[config['Custom Field for Ending date']].date():
                j[name] += int(l[config['Custom Field with hours per month']])/30.4
        for k in categories:
            j[k] = 0
        for l,m in kaarten.items():
            if m[config['Custom Field for Categories']] in categories:
                if m['status'] not in ['Archived','Done']:
                    try:
                        if m[config['Custom Field for Starting date']].date() <= datekey <= m[config['Custom Field for Ending date']].date():
                            j[m[config['Custom Field for Categories']]] += int(m[config['Custom Field with hours per month']])/30.4
                    except:
                        pass


# ### Create extra dictionaries to dump to JSON later

# In[ ]:


statuslist = []
for i,j in kaarten.items():
    statuslist.append(j['status'])
statuslist = list(dict.fromkeys(statuslist))


# In[ ]:


statuses = []
for i,j in config.items():
    if type(j) == list:
        for k in j:
            statuses.append((k,i))


# In[ ]:


for i,j in datesdict.items():
    datekey = datetime.strptime(i, '%Y-%m-%d').date()
    for k in statuslist:
        j[str('Status ' + k)] = 0
    for k,l in j.items():
        for m in statuses:
            if k == m[0]:
                j[str('Status ' + m[1])] += l


# ### If all values are zero for a date, that date is useless, so deleting..

# In[ ]:


datetodelete = []
for i,j in datesdict.items():
    j['count'] = 0
    for k in chosenlists:
        j['count'] += j.get(k)
    if config['Script options'].get('Calculate hours') == True:
        for k in categories:
            j['count'] += j.get(k)
    if j['count'] == 0:
        datetodelete.append(i)
    del j['count']
for i in datetodelete:
    if i in datesdict:
        del datesdict[i]


# ### Create a few extra fields with dates and determine these dates with the list movements

# In[ ]:


for i,j in kaarten.items():
    j['datedone'] = None
    j['datestarted'] = None
    j['datelastblocked'] = None
    j['datelastunblocked'] = None

    if j['status'] == 'Done':
        tmp = []
        for k,l in j['movements'].items():
            if l['listAfter'] in config['Done']:
                tmp.append(k)
        j['datedone'] = max(tmp)

    if j['status'] != 'Done' or 'Archived':
        tmp = []
        for k,l in j['movements'].items():
            if l['listAfter'] in config['Doing']:
                tmp.append(k)
        if tmp != []:
            j['datestarted'] = min(tmp)

    if j['datestarted'] == None:
        if j['status'] != 'Archived':
            if j['status'] != 'Not started':
                j['datestarted'] = j['created']
    tmp = []
    if j['status'] != 'Blocked':
        for k,l in j['movements'].items():
            if l['listBefore'] in config['Blocked']:
                tmp.append(k)
                j['datelastunblocked'] = max(tmp)
    tmp = []
    for k,l in j['movements'].items():
        if l['listAfter'] in config['Blocked']:
            tmp.append(k)
            j['datelastblocked'] = max(tmp)


# ### Create a temporary list with all dates from the Dates dictionary

# In[ ]:


datelist = []
for i in datesdict.keys():
    datelist.append(i)


# ### Create a dictionary for in and out and determine values with dates already in the cards dictionary

# In[ ]:


in_out = {}
for i in datelist:
    in_out[i]= {}
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
for i,j in datesdict.items():
    for k,l in in_out.items():
        if i==k:
            j['In'] = l['In']
            j['Out'] = l['Out']


# # NEW

# In[ ]:


jsoncards = {}
for i,j in kaarten.items():
    del j['listmovements']
    del j['movements']
    jsoncards[i] = {}
    for k,l in j.items():
        if type(l) == datetime:
            jsoncards[i][k] = 'date, ' + l.strftime("%Y-%m-%d, %H:%M:%S")
        else:
            jsoncards[i][k] = l


# In[ ]:


def dumpjson(file, data):
    with open('./data/'+file, 'w') as outfile:
        json.dump(data, outfile, indent=4, sort_keys=True)


# In[ ]:


dumpjson('customfields.json', customfields_dict)
dumpjson('chosenlists.json', chosenlists)
dumpjson('statuses.json', statuses)
dumpjson('statuslist.json', statuslist)
dumpjson('members.json', members)
dumpjson('labels.json', labels)
dumpjson('kaarten.json', jsoncards)
dumpjson('timeline.json', datesdict)


# In[ ]:


string = datetime.now().strftime("%Y-%m-%d, %H:%M:%S")
text_file = open("./data/date.txt", "w")
n = text_file.write(string)
text_file.close()

