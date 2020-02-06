#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os,json,pprint


# In[ ]:


if os.path.exists('configuration.txt'):
    with open('configuration.txt') as json_file:
        config = json.load(json_file)
else:
    config = {
        'boardid': '',
        'notstarted': [],
        'blocked': [],
        'doing': [],
        'done': [],
        'excelfile': '',
        'toaddr': '',
        'subj': '',
        'spreadsheetid': '',
        'timelinesheet': '',
        'alldatasheet': '',
        'googlejsonfile': '',
        'scriptoptions': {'excelalldata': False,
                          'gspreadalldata': False,
                          'exceltimeline': False,
                          'gspreadalldata': False,
                          'gspreadtimeline': False,
                          'cleandonelists': False
                   }
    }
if os.path.exists('credentials.txt'):
    with open('credentials.txt') as json_file:
        credentials = json.load(json_file)
else:
    credentials = {
        'api_key': '',
        'api_token': '',
        'gmail': '',
        'gpassword': ''   
    }


# In[ ]:


def createfile(file,data):
    if not os.path.exists(file):
        with open(file, 'w') as outfile:
            json.dump(data, outfile)
    else:
        answer = input('File already exists. Overwrite? (y/n)')
        if answer.lower() == 'y':
            print('Saving..')
            updatefile(file,data)
        else:
            print('Not saved!')
def updatefile(file,data):
    with open(file,'w') as outfile:
        json.dump(data,outfile, indent=4, sort_keys=True)
def removefile(file):
    os.remove(file)
    
def saveconfig():
    answer = input('Save current config? (y/n)')
    if answer.lower() == 'y':
        print('Saving..')
        updatefile('configuration.txt',config)
    else:
        answer2 = input('Are you sure? (y/n)')
        if answer2.lower() != 'y':
            saveconfig()
def savecreds():
    answer = input('Save current credentials? (y/n)')
    if answer.lower() == 'y':
        print('Saving..')
        updatefile('credentials.txt',credentials)
    else:
        answer2 = input('Are you sure? (y/n)')
        if answer2.lower() != 'y':
            savecreds()

def my_quit_fn():
    saveconfig()
    savecreds()
    
    
def invalid():
    print ("INVALID CHOICE!")

def updatejson(key,dictionary):
    print()
    if type(dictionary.get(key)) == list:
        print('current value: ', dictionary[key])
        value = input('give ' + key + ', comma separated (ex1,ex2,ex3)')
        dictionary[key] = value.split(',')
    elif type(dictionary.get(key)) == dict:
        updatejsondict(dictionary,key)
    else:
        print('current value: ', dictionary[key])
        value = input('give ' + key)        
        dictionary[key] = value
    print('new value: ', dictionary[key])

def updatejsondict(dictionary,key):
    print()
    options = {}
    x = 1
    for i,j in dictionary[key].items():
        options[str(x)] = (i)
        x += 1
    options['98'] = ('Back to main menu')
    options['99'] = ('Quit')
    print('Set boolean values for: ')
    for i in options.keys():
        if 1 <= int(i) <= 60:
            print(i+": "+options[i])
    print()
    print('Other options')
    for i in options.keys():
        if int(i)>60:
            print(i+": "+ options[i])    
    ans = input("Make A Choice")
    if not ans in options.keys():
        invalid()
        updatejsondict(dictionary,key)
    else:
        value = input('Set value (0=disable, 1=enable)')
        enabledisable(value,options.get(ans),dictionary,key)

def enabledisable(answer,option,dictionary,key):
    if answer == '1':
        dictionary[key][option] = True
    elif answer == '0':
        dictionary[key][option] = False
    else:
        invalid()
        enabledisable(value,options.get(ans))


# ### Create menu

# In[ ]:


def mainmenu():
    print()
    print('Main menu')
    print()
    options = {}
    options['1'] = ("Print current config file")
    options['2'] = ('Print current credentials file')
    options['3'] = ('Write empty config file')
    options['4'] = ('Write empty credentials file')
    options['5'] = ('Delete config file')
    options['6'] = ('Delete credentials file')
    options['7'] = ('Set configuration')
    options['8'] = ('Set credentials')
    options['99'] = ('Quit')
    for i in options.keys():
        print(i+": "+options[i]) 
    ans = input('Make a choice')
    if ans not in options.keys():
        invalid()
        mainmenu()
    else:
        if ans == '99':
            my_quit_fn()
        else:
            if ans == '1':
                pprint.pprint(config)
            elif ans == '2':
                pprint.pprint(credentials)
            elif ans == '3':
                createfile('configuration.txt',config)
            elif ans == '4':
                createfile('credentials.txt', credentials)
            elif ans == '5':
                os.remove('configuration.txt')
            elif ans == '6':
                os.remove('credentials.txt')
            elif ans == '7':
                editor(config)
            elif ans == '8':
                editor(credentials)
            mainmenu()


# ### Create submenu to edit config

# In[ ]:


def editor(dicttochange):
    print()
    print('Change values')
    print()
    editconfig = {}
    x=1
    availableoptions = []
    for i in dicttochange.keys():
        editconfig[str(x)] = (i)
        availableoptions.append(str(x))
        x += 1
    editconfig['98'] = ('Back to main menu')
    editconfig['99'] = ('Quit')
    for i in editconfig.keys():
        if 1 <= int(i) <= 60:
            print(i+": "+editconfig[i])
    print()
    print('Other options')
    for i in editconfig.keys():
        if int(i)>60:
            print(i+": "+editconfig[i])
    ans = input('Make a choice')
    if ans in editconfig.keys():
        if ans == '99':
            my_quit_fn()
        elif ans == '98':
            mainmenu()
        elif editconfig.get(ans) == 'spreadsheetid':
            googlesheetsconfig()
        else:
            try:
                updatejson(editconfig.get(ans),dicttochange)
            except:
                invalid()
    else:
        invalid()
        editor(dicttochange)


# In[ ]:


def googlesheetsconfig():
    import pandas as pd
    import gspread
    import df2gspread as d2g
    
    print ('First go to: https://gspread.readthedocs.io/en/latest/oauth2.html')
    print('And follow instructions to download the JSON.')
    print('Place the JSON into the same folder as this script.')
    jsonfilefromgoogle = input('Give the name for the JSON (ex.: jsonFileFromGoogle.json)')
    config['jsonfilefromgoogle'] = jsonfilefromgoogle
    spreadsheetid = spreadsheeturltoid(input('Create a new Sheets File and paste the URL.'))
    config['spreadsheetid'] = spreadsheetid
    with open(jsonfilefromgoogle) as json_file:
        googlecreds = json.load(json_file)
    config['googleclientemail'] = googlecreds.get('client_email')
    print('Share your spreadsheet with '+ '\''+googlecreds.get('client_email')+'\'')
    
def spreadsheeturltoid(url):
    spreadsheetid = url.strip('https://docs.google.com/spreadsheets/d/')
    x=0
    tmp = []
    for i in spreadsheetid:
        tmp.append((x,i))
        x += 1
    for i,j in tmp:
        if j == '/':
            stop = i
            break
    return spreadsheetid[0:stop]


# In[ ]:


mainmenu()

