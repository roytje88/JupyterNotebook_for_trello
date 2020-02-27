#!/usr/bin/env python
# coding: utf-8

#exec(open("./creategraphdata.py").read())
configurationfile = './configuration/configuration.txt'
credentialsfile = './configuration/credentials.txt'
import os,json
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


import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import datetime
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor











# number of seconds between re-calculating the data
UPDADE_INTERVAL = 5

def get_new_data():
    """Updates the global variable 'data' with new data"""
    global graphdata
    global listfig
    global statusfig

    def loadjson(file):
        with open('./data/'+file) as json_file:
            return json.load(json_file)



    chosenlists = loadjson('chosenlists.json')
    graphdata = loadjson('graphdata.json')
    statuses = loadjson('statuses.json')
    statuslist = loadjson('statuslist.json')


    layout = go.Layout(barmode='stack')

    x = 0
    for i in statuslist:
        if x == 0:
            if i != 'Archived':
                statusfig = go.Figure(layout=layout, data=[go.Bar(name=i, x = graphdata.get('dates'), y = graphdata.get('Status '+i))])
                x = 1
                first = 'Status ' + i

    for i,j in graphdata.items():
        if i[:7] == 'Status ':
            if i != first:
                statusfig.add_trace(go.Bar(name=i[7:],x=graphdata.get('dates'),y=j))




    listfig = go.Figure(layout=layout, data=[go.Bar(name=chosenlists[0],x = graphdata.get('dates'), y=graphdata.get(chosenlists[0]))])

    for i in chosenlists:
        if i != chosenlists[0]:
            listfig.add_trace(go.Bar(name=i,x=graphdata.get('dates'),y=graphdata.get(i)))
    return listfig
    return statusfig





def get_new_data_every(period=UPDADE_INTERVAL):
    """Update the data every 'period' seconds"""

    while True:
        get_new_data()
        time.sleep(period)


def make_layout():
    return html.Div(children=[
        html.H1(children='Werkvoorraad'),
        html.Div('Last update: ' + str(datetime.datetime.now())),
        html.Div(children='''
            Tijdlijn per lijst
        '''),

        dcc.Graph(figure=listfig),
        html.Div(children='''
            Tijdlijn per status
        '''),
        dcc.Graph(figure=statusfig)
    ])

app = dash.Dash(__name__)

# get initial data
get_new_data()

# we need to set layout to be a function so that for each new page load
# the layout is re-created with the current data, otherwise they will see
# data that was generated when the Dash app was first initialised
app.layout = make_layout

# Run the function in another thread
executor = ThreadPoolExecutor(max_workers=1)
executor.submit(get_new_data_every)


if __name__ == '__main__':
    app.run_server(debug=True)
