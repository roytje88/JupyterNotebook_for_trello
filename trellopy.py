#!/usr/bin/env python
# coding: utf-8

# ## Import libraries

# In[ ]:


import requests,json,os, pprint,requests
import pandas as pd
from datetime import date,datetime,timedelta


# ### Set configuration files

# In[ ]:


configurationfile = './configuration/configuration.txt'
credentialsfile = './configuration/credentials.txt'


# ### Load configuration and credentials

# In[ ]:


def loadconfig():
    global config
    global credentials
    if os.path.exists(configurationfile):
        with open(configurationfile) as json_file:
            config = json.load(json_file)
    else:
        print('No configuration found. To create one, run Setup!')

    if os.path.exists(credentialsfile):
        with open(credentialsfile) as json_file:
            credentials = json.load(json_file)
    else:
        print('No credentials found. To create one, run Setup!')
loadconfig()


# ### Open all options

# In[ ]:


with open('credentialsoptions.txt') as json_file:
    credentialsoptions = json.load(json_file)
with open('configoptions.txt') as json_file:
    configoptions = json.load(json_file)


# ### Create function to convert config file

# In[ ]:


def updateconfig(file,olddict,newdict):
    newconfig = {}
    newconfig['Version'] = newdict['Version']
    ans = input('Old ' + file[16:] + ' found. Update now?')
    if ans.upper() != 'N':
        print('This is your old config:')
        pprint.pprint(olddict)
        for i,j in newdict.items():
            if i != 'Version':
                if type(j)== list:
                    newconfig[i] = []
                    value = input('Give the number of lists to add for the status '+i)
                    if value != '':
                        try:
                            x = int('Input one list each time for list '+value)
                        except:
                            x = int(input('Not an integer. Please try again.'))
                        count = 1
                        if x != 0:
                            while count <= x:
                                newconfig[i].append(input(i))
                                count += 1
                elif type(j) == dict:
                    newconfig[i] = {}
                    for k,l in j.items():
                        if type(l) == bool:
                            answer = input(k + ' (Y/N)').upper()
                            if answer == 'Y':
                                newconfig[i][k] = True
                            else:
                                newconfig[i][k] = False
                        else:
                            newconfig[i][k] = input(k)
                else:
                    newconfig[i] = input(i)
        with open(file, 'w') as outfile:
            json.dump(newconfig,outfile, indent=4, sort_keys=True)
    else:
        pass


# ### Check which version of the configuration is loaded and ask to update it

# In[ ]:


try:
    version = float(config['Configuration version'])
except:
    version = 0.0
if version == 0.0:
    updateconfig(configurationfile, config, configoptions)
    loadconfig()
try:
    version = float(credentials['Configuration version'])
except:
    version = 0.0
if version == 0.0:
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
                j[customfields_dict['date'][k['idCustomField']].get('name')] = dateCalc(k['value'].get('date'))
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
        j['status'] = 'Not started'
    elif j['list'] in config.get('Doing'):
        j['status'] = 'Doing'
    elif j['list'] in config.get('Blocked'):
        j['status'] = 'Blocked'
    elif j['list'] in config.get('Done'):
        j['status'] = 'Done'
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
numdays = 400

for x in range (0, numdays):
    datesdict[str(now - timedelta(days = x))] = {}


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


# ### If all values are zero for a date, that date is useless, so deleting..

# In[ ]:


datetodelete = []
for i,j in datesdict.items():
    j['count'] = 0
    for k in chosenlists:
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


# ### Create function to ouput all cards to excel

# In[ ]:


def excelalldata():
    import pandas as pd
    labelslist = []
    for i,j in kaarten.items():
        for k,l in j.items():
            if k=='labels' and l != {}:
                for m,n in l.items():
                    labelslist.append((i,n))
    memberslist = []
    for i,j in kaarten.items():
        for k,l in j.items():
            if k=='members' and l !={}:
                for m,n in l.items():
                    memberslist.append((i,n))
    if labelslist != []:
        columnslabels = ['cardid','label']
        columnsmembers = ['cardid','member']
        df1 = pd.DataFrame(data=kaarten).T
        df2 = pd.DataFrame(data=labelslist,columns=columnslabels)
        df3 = pd.merge(df1,df2,on='cardid', how='left')
        df4 = pd.DataFrame(data=memberslist,columns=columnsmembers)
        df5 = pd.merge(df3,df4,on='cardid', how='left')
        df5.to_excel(config.get('excelfile'))
    else:
        columnsmembers = ['cardid','member']
        df1 = pd.DataFrame(data=kaarten).T
        df2 = pd.DataFrame(data=memberslist,columns=columnsmembers)
        df3 = pd.merge(df1,df2,on='cardid', how='left')
        df3.to_excel(config.get('excelfile'))


# ### Create function to output the timeline to excel (WIP)

# In[ ]:


def exceltimeline():
    print('exceltimeline is not defined yet.')


# ### Create function to output the timeline to Google Sheets

# In[ ]:


def timelinetosheets(dictionary,sheetid,worksheet):
    jsonfile = './configuration/'+config['JSON file from Google']
    import gspread
    from df2gspread import df2gspread as d2g
    import oauth2client
    from oauth2client.service_account import ServiceAccountCredentials
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    gcredentials = ServiceAccountCredentials.from_json_keyfile_name(jsonfile , scope)

    client = gspread.authorize(gcredentials)
    wks = client.open_by_key(sheetid)
    x = 0
    sheetnames = []
    try:
        while wks.get_worksheet(x) != None:
            sheetnames.append(wks.get_worksheet(x).title)
            x += 1
    except:
        pass
    if not worksheet in sheetnames:
        tempwks = wks.add_worksheet(title=worksheet, rows="1000", cols="30")

    dataframe = pd.DataFrame(data=dictionary).T
    d2g.upload(dataframe, sheetid, worksheet, credentials=gcredentials, row_names=True)
    sheet = wks.worksheet(worksheet)
    sheet.update_acell('A1', 'Date')


# ### Create function to output all data to Google Sheets

# In[ ]:


def alldatatosheets(dictionary,sheetid,worksheet):
    jsonfile = './configuration/'+config['JSON file from Google']
    import gspread
    from df2gspread import df2gspread as d2g
    import oauth2client
    from oauth2client.service_account import ServiceAccountCredentials
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    gcredentials = ServiceAccountCredentials.from_json_keyfile_name(jsonfile , scope)

    client = gspread.authorize(gcredentials)
    wks = client.open_by_key(sheetid)
    x = 0
    sheetnames = []
    try:
        while wks.get_worksheet(x) != None:
            sheetnames.append(wks.get_worksheet(x).title)
            x += 1
    except:
        pass
    if not worksheet in sheetnames:
        tempwks = wks.add_worksheet(title=worksheet, rows="1000", cols="30")

    labelslist = []
    for i,j in dictionary.items():
        for k,l in j.items():
            if k=='labels' and l != {}:
                for m,n in l.items():
                    labelslist.append((i,n))
    memberslist = []
    for i,j in dictionary.items():
        for k,l in j.items():
            if k=='members' and l !={}:
                for m,n in l.items():
                    memberslist.append((i,n))
    for i,j in dictionary.items():
        try:
            del j['labels']
        except:
            pass
    if labelslist != []:
        columnslabels = ['cardid','label']
        columnsmembers = ['cardid','member']
        df1 = pd.DataFrame(data=kaarten).T
        df2 = pd.DataFrame(data=labelslist,columns=columnslabels)
        df3 = pd.merge(df1,df2,on='cardid', how='left')
        df4 = pd.DataFrame(data=memberslist,columns=columnsmembers)
        dataframe = pd.merge(df3,df4,on='cardid', how='left')


    else:
        columnsmembers = ['cardid','member']
        df1 = pd.DataFrame(data=kaarten).T
        df2 = pd.DataFrame(data=memberslist,columns=columnsmembers)
        dataframe = pd.merge(df1,df2,on='cardid', how='left')

    d2g.upload(dataframe, sheetid, worksheet, credentials=gcredentials, row_names=True)


# ### Create function to archive cards older than set in configuration

# In[ ]:


def cleandonelists():
    maxdatetime = datetime.now() - timedelta(days = int(config['maxdaysindone']))
    for i,j in kaarten.items():
        if j['status'] == 'Done' and j['closed'] == False:
            if j['datedone'] < maxdatetime:
                url = "https://api.trello.com/1/cards/"+i
                querystring = {"closed":"true","key":credentials.get('api_key'),"token":credentials.get('api_token')}
                response = requests.request("PUT", url, params=querystring)
                response


# ### Create function to remove members of cards in Done

# In[ ]:


def removemembers():
    for i,j in kaarten.items():
        if j['status'] in ['Done','Archived']:
            try:
                for k,l in j['members'].items():
                    url = 'https://api.trello.com/1/cards/'+i+'/idMembers/'+k
                    querystring = {"closed":"true","key":credentials.get('api_key'),"token":credentials.get('api_token')}
                    response = requests.request('DELETE', url, params=querystring)
                    response
            except:
                pass


# ### Run all function with value True in the configuration

# In[ ]:


if config['Script options']['Output all data to Excel'] == True:
    print('Not scripted yet.')
#    excelalldata()
if config['Script options']['Output a timeline to Excel'] == True:
    print('Not scripted yet.')    
#    exceltimeline()
if config['Script options']['Output all data to Google Sheets'] == True:
    alldatatosheets(kaarten,config['Google Spreadsheet ID'],config['Google sheetname for all Trello data'])
if config['Script options']['Output a timeline to Google Sheet'] == True:
    timelinetosheets(datesdict,config['Google Spreadsheet ID'],config['Google sheetname for timeline'])
if config['Script options']['Clean the Done lists'] == True:
    cleandonelists()
if config['Script options']['Remove members from Done and Archived cards'] == True:
    removemembers()

