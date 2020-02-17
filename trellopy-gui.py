from PyQt5.QtWidgets import QApplication, QLabel, QTreeWidget, QTreeWidgetItem, QCheckBox, QTableWidgetItem
from PyQt5 import uic, QtWidgets
import sys,os,pprint,json,requests
import pandas as pd
from datetime import date,datetime,timedelta

### FUNCTIONS

def createfolders():
    try:
        temp = os.stat('./configuration')
    except:
        os.mkdir('./configuration')

configurationfile = './configuration/configuration.txt'
credentialsfile = './configuration/credentials.txt'

def loadconfig():
    global configoptions
    global config
    global configfound
    global credentials
    global credentialsfound
    global credentialsoptions
    global allconfig
    global statuses

    configoptions = {
            'Board ID': '',
            'Not Started': [],
            'Blocked': [],
            'Doing': [],
            'Done': [],
            'Excel Outputfile': '',
            'Email address to send': '',
            'Subject of Email': '',
            'Google Spreadsheet ID': '',
            'Google sheetname for timeline': '',
            'Google sheetname for all Trello data': '',
            'JSON file from Google': '',
            'Maximum days a card can be in Done': '',
            'Script options': {'Output all data to Excel': False,
                              'Output all data to Google Sheets': False,
                              'Output a timeline to Excel': False,
                              'Output a timeline to Google Sheet': False,
                              'Clean the Done lists': False,
                              'Remove members from Done and Archived cards': False
                       }
        }
    credentialsoptions = {
            'API key': '',
            'API token': '',
            'Gmail Address': '',
            'Gmail password': ''
        }
    if os.path.exists(configurationfile):
        with open(configurationfile) as json_file:
            config = json.load(json_file)
        configfound=True
    else:
        config = {}
        for i,j in configoptions.items():
            config[i] = j
        configfound=False

    if os.path.exists(credentialsfile):
        with open(credentialsfile) as json_file:
            credentials = json.load(json_file)
        credentialsfound=True
    else:
        credentials = {}
        for i,j in credentialsoptions.items():
            credentials[i] = j
        credentialsfound=False

    allconfig = {}
    def writevaluestotable(key,value):
       allconfig[key] = value





    statuses = ['Not Started','Blocked','Doing','Done']

    allconfig = {}
    def writevaluestotable(key,value):
       allconfig[key] = value

    def unpackvalues(item, parent=None):
        if type(item) is dict:
            for i,j in item.items():
                unpackvalues(j,i)
        else:
            if parent != None:
                if not parent in statuses:
                    if type(item) is list:

                        for i in item:
                            unpackvalues(i,parent)
                    else:
                        writevaluestotable(parent,item)
    unpackvalues(configoptions)
    unpackvalues(credentialsoptions)
    unpackvalues(config)
    unpackvalues(credentials)


def updatefile(file,data):
    try:
        for i,j in data.items():
            if i in statuses:
                data[i] = list(dict.fromkeys(j))
    except:
        pass

    with open(file,'w') as outfile:
        json.dump(data,outfile, indent=4, sort_keys=True)


def writetoconfig():
    for i,j in allconfig.items():
        for k,l in config.items():
            if type(l) is list:
                if i == k:
                    if j not in l:

                        config[i].append(j)
            elif type(l) is dict:
                for m,n in l.items():
                    if i == m:
                        config[k][i] = j
            else:
                if i == k:
                    config[i] = j
        for k,l in credentials.items():
            if i == k:
                credentials[i] = j
    updatefile(configurationfile,config)
    updatefile(credentialsfile,credentials)

def updatestatuses():
    statussen = {}
    for i in statuses:
        statussen[i] = []
    for i,j in listswithstatuses.items():
        if j in statussen.keys():
            statussen[j].append(i)
    for i,j in config.items():
        if i in statuses:
            config[i] = statussen.get(i)
    updatefile(configurationfile,config)
    updatefile(credentialsfile,credentials)

createfolders()

loadconfig()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('mainwindow.ui', self)
        self.show()

        ## Get all attributes

        self.apikey = self.findChild(QtWidgets.QLineEdit, 'apikey')
        self.apitoken = self.findChild(QtWidgets.QLineEdit, 'apitoken')
        self.getboardsbtn = self.findChild(QtWidgets.QPushButton, 'getboardsbtn')
        self.setstatusbtn = self.findChild(QtWidgets.QPushButton, 'setstatusbtn')

        self.cleandonebtn = self.findChild(QtWidgets.QPushButton, 'cleandonebtn')
        self.timelineexcelbtn = self.findChild(QtWidgets.QPushButton, 'timelineexcelbtn')
        self.timelinegsheetsbtn = self.findChild(QtWidgets.QPushButton, 'timelinegsheetsbtn')
        self.alldataexcelbtn = self.findChild(QtWidgets.QPushButton, 'alldataexcelbtn')
        self.alldatagsheetsbtn = self.findChild(QtWidgets.QPushButton, 'alldatagsheetsbtn')
        self.removemembersbtn = self.findChild(QtWidgets.QPushButton, 'removemembersbtn')

        self.comboboxboards = self.findChild(QtWidgets.QComboBox, 'comboboxboards')
        self.comboboxstatus = self.findChild(QtWidgets.QComboBox, 'comboboxstatus')
        self.comboboxlist = self.findChild(QtWidgets.QComboBox, 'comboboxlist')
        self.liststable = self.findChild(QtWidgets.QTableWidget, 'liststable')
        self.optionvalue = self.findChild(QtWidgets.QLineEdit, 'optionvalue')
        self.setoptionbtn = self.findChild(QtWidgets.QPushButton, 'setoptionbtn')
        self.optionstable = self.findChild(QtWidgets.QTableWidget, 'optionstable')
        self.comboboxoption = self.findChild(QtWidgets.QComboBox, 'comboboxoption')

        ## Assign attributes to actions

        self.getboardsbtn.clicked.connect(self.getboards)
        self.setstatusbtn.clicked.connect(self.setstatus)
        self.comboboxstatus.currentTextChanged.connect(self.status_combobox_changed)
        self.comboboxboards.currentTextChanged.connect(self.board_combobox_changed)
        self.comboboxlist.currentTextChanged.connect(self.list_combobox_changed)
        self.setoptionbtn.clicked.connect(self.setoption)
        self.comboboxoption.currentTextChanged.connect(self.option_combobox_changed)

        self.cleandonebtn.clicked.connect(test)
        self.timelineexcelbtn.clicked.connect(test)
        self.timelinegsheetsbtn.clicked.connect(timelinetosheets)
        self.alldataexcelbtn.clicked.connect(test)
        self.alldatagsheetsbtn.clicked.connect(alldatatosheets)
        self.removemembersbtn.clicked.connect(test)




        try:
            if credentials['API key'] != "":
                self.apikey.setText(credentials['API key'])
            if credentials['API token'] != "":
                self.apitoken.setText(credentials['API token'])
        except:
            pass



        # Run method to fill the statuses
        self.fillstatusbox()
        self.getoptions()

        ## Create methods for actions

    def getboards(self):
        try:
            self.comboboxboards.clear()
        except:
            pass
        global allboards
        apikey = self.apikey.text()
        apitoken = self.apitoken.text()
        url = 'https://api.trello.com/1/members/me/boards?key='+apikey+'&token='+apitoken
        boards = json.loads(json.dumps(requests.get(url).json()))
        allboards = []
        for i in boards:
            if i['closed'] != True:
                allboards.append((i['id'],i['name']))
        for i in allboards:
            self.comboboxboards.addItem(i[1])
        self.filloptionstable()
        credentials['API key'] = apikey
        credentials['API token'] = apitoken
        updatefile(credentialsfile,credentials)

    def board_combobox_changed(self, value):
        global boardid
        if value != None:
            for i in allboards:
                if i[1] == value:
                    boardid = i[0]
                    config['Board ID'] = boardid
                    writetoconfig()
                    self.filloptionstable()
        else:
            boardid = None
        self.getlists()

    def getlists(self):
        try:
            self.comboboxlist.clear()
        except:
            pass
        global alllists
        apikey = self.apikey.text()
        apitoken = self.apitoken.text()
        url = 'https://api.trello.com/1/boards/'+boardid+'/lists?key='+apikey+'&token='+apitoken
        lists = json.loads(json.dumps(requests.get(url).json()))
        alllists = []
        for i in lists:
            if i['closed'] != True:
                alllists.append(i['name'])
                self.comboboxlist.addItem(i['name'])
        self.getlistswithstatuses()

    def fillstatusbox(self):
        self.comboboxstatus.addItem(None)
        for i in statuses:
            self.comboboxstatus.addItem(i)

    def getlistswithstatuses(self):
        global listswithstatuses
        listswithstatuses = {}
        listsinconfig = {}
        for i,j in config.items():
            if i in statuses:
                for k in j:
                    listsinconfig[k] = i

        for i in alllists:
            listswithstatuses[i] = None
        for j,k in listsinconfig.items():
            listswithstatuses[j] = k


        self.fillliststable()

    def fillliststable(self):
        try:
            count = self.liststable.rowCount()-1
            while count >= 0:
                self.liststable.removeRow(count)
                count -= 1
        except:
            pass
        for i,j in listswithstatuses.items():
            rowPosition = self.liststable.rowCount()
            header = self.liststable.horizontalHeader()
            header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
            self.liststable.insertRow(rowPosition)
            self.liststable.setItem(rowPosition , 0, QTableWidgetItem(i))
            self.liststable.setItem(rowPosition , 1, QTableWidgetItem(j))

    def setstatus(self):
        listswithstatuses[listname] = status
        updatestatuses()
        self.getlists()
        self.filloptionstable()

    def getoptions(self):
        try:
            self.comboboxoption.clear()
        except:
            pass
        for i in allconfig.keys():
            self.comboboxoption.addItem(i)


    def filloptionstable(self):
        try:
            count = self.optionstable.rowCount()-1
            while count >= 0:
                self.optionstable.removeRow(count)
                count -= 1
        except:
            pass
        loadconfig()
        header = self.optionstable.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        for i,j in allconfig.items():
            rowPosition = self.optionstable.rowCount()

            self.optionstable.insertRow(rowPosition)
            self.optionstable.setItem(rowPosition , 0, QTableWidgetItem(i))
            self.optionstable.setItem(rowPosition , 1, QTableWidgetItem(j))


    def setstatus(self):
        listswithstatuses[listname] = status
        updatestatuses()
        self.fillliststable()


    def status_combobox_changed(self, value):
        global status
        if value != None:
            status = value

    def board_combobox_changed(self, value):
        global boardid
        if value != None:
            for i in allboards:
                if i[1] == value:
                    boardid = i[0]
        else:
            boardid = None
        self.getlists()
        allconfig['Board ID'] = boardid
        writetoconfig()
        self.filloptionstable()

    def list_combobox_changed(self, value):
        global listname
        if value != None:
            listname = value

    def setoption(self):
        newvalue = self.optionvalue.text()
        allconfig[option] = newvalue
        writetoconfig()
        loadconfig()
        self.filloptionstable()

    def option_combobox_changed(self, value):
        global option
        if value != None:
            option = value
        self.filloptionstable()

def createdata():

    def createurls():
        global board_url
        global url_cards
        global url_lists
        global url_customfields
        global url_labels
        global url_members
        global keys
        keys = "key="+credentials.get('API key')+"&token="+credentials.get('API token')
        trello_base_url = "https://api.trello.com/1/"
        board_url = trello_base_url+"boards/"+config.get('Board ID')
        url_cards = board_url+"/cards?attachments=true&customFieldItems=true&filter=all&"+keys
        url_lists = board_url+"/lists?filter=all&"+keys
        url_customfields = board_url+"/customFields?"+keys
        url_labels = board_url+"/labels?"+keys
        url_members = board_url+"/members?"+keys

    createurls()


    def getjson():
        global cards
        global lists
        global customfields
        global labels
        global members
        cards = json.loads(json.dumps(requests.get(url_cards).json()))
        lists = json.loads(json.dumps(requests.get(url_lists).json()))
        customfields = json.loads(json.dumps(requests.get(url_customfields).json()))
        labels = json.loads(json.dumps(requests.get(url_labels).json()))
        members = json.loads(json.dumps(requests.get(url_members).json()))

    getjson()

    def dateCalc(date):
        newdate = datetime.strptime(date[0:19],'%Y-%m-%dT%H:%M:%S')
        return newdate

    def idtodate(cardid):
        hex = cardid[0:8]
        timestamp = int(hex,16)
        timedate = datetime.fromtimestamp(timestamp)
        return timedate

    def createcustomfields_dict():
        global customfields_dict
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

    createcustomfields_dict()

    def createchosenlists():
        global chosenlists
        chosenlists = []
        for i in config.get('Not Started'):
            chosenlists.append(i)
        chosenlists.extend(config.get('Blocked'))
        chosenlists.extend(config.get('Doing'))
        chosenlists.extend(config.get('Done'))

    createchosenlists()

    def createkaarten():
        global kaarten
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

    createkaarten()


    def addcustomfields():
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

    if customfields_dict != {}:
        addcustomfields()
    else:
        pass

    def addstatustokaarten():
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

    addstatustokaarten()


    def archivedcards():
        for i,j in kaarten.items():
            if j['closed'] == True and j['status'] != 'Done':
                j['status'] = 'Archived'

    archivedcards()

    def removecardsfromdict():
        liststodelete = []
        for i in lists:
            if i['name'] not in chosenlists:
                liststodelete.append(i['name'])
        cardstodelete = []
        for i,j in kaarten.items():
            if j['sjabloon'] == True:
                cardstodelete.append(i)
            elif j['list'] in liststodelete:
                cardstodelete.append(i)
        for i in cardstodelete:
            if i in kaarten:
                del kaarten[i]

    removecardsfromdict()

    def getactions():
        global actions
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


    getactions()

    def addactions():
        for n,o in kaarten.items():
            o['actions'] = []
            for i in actions:
                for j,k in i.items():
                    if j == 'data':
                        for l,m in k.items():
                            if l == 'card':
                                if n == m['id']:
                                    o['actions'].append(i)

    addactions()

    def addlistmovements():
        global historicallists
        for i,j in kaarten.items():
            j['listmovements'] = {}
            for k in j['actions']:
                for l,m in k.items():
                    try:
                        j['listmovements'][dateCalc(k['date'])] = {'listAfter': k['data']['listAfter']['id'], 'listBefore': k['data']['listBefore']['id']}
                    except:
                        pass
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
        historicallists = []
        historicallists.extend(chosenlists)

        for i,j in kaarten.items():
            for k,l in j['movements'].items():
                for m,n in l.items():
                    for o in lists:
                        if o['id'] == n:
                            l[m] = o['name']
                            historicallists.append(o['name'])

    addlistmovements()

    def createdatesdict():
        global datesdict
        global now
        datesdict = {}
        now = datetime.now().date()
        numdays = 400

        for x in range (0, numdays):
            datesdict[str(now - timedelta(days = x))] = {}

    createdatesdict()

    def filldatesdict():
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

    filldatesdict()

    def createextradatescolumns():
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

    createextradatescolumns()

    def addinout():
        datelist = []
        for i in datesdict.keys():
            datelist.append(i)
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

    addinout()





# createdata()

def test():
    print('Not Ready!')

def checkifdataisready():
    try:
        test = kaarten
    except:
        createdata()


def excelalldata():
    checkifdataisready()
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
        df3.to_excel(config.get('Excel Outputfile'))


def exceltimeline():
    print('exceltimeline is not defined yet.')


def alldatatosheets():
    checkifdataisready()
    sheetid = config['Google Spreadsheet ID']
    jsonfile = './configuration/'+config['JSON file from Google']
    dictionary = kaarten
    worksheet = config['Google sheetname for all Trello data']
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


def timelinetosheets():
    checkifdataisready()
    sheetid = config['Google Spreadsheet ID']
    jsonfile = './configuration/'+config['JSON file from Google']
    dictionary = datesdict
    worksheet = config['Google sheetname for timeline']
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











## RUN QT5
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    MW = MainWindow()
    MW.show()
    sys.exit(app.exec_())
