#!/usr/bin/env python
# coding: utf-8

exec(open("./trellopy.py").read())

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

layout = go.Layout(barmode='stack')

fig = go.Figure(layout=layout, data=[go.Bar(name=chosenlists[0],x=x,y=Nieuw)])
for i in chosenlists:
    if i != chosenlists[0]:
        if i not in config.get('Done'):
            listname = i.replace(' ','_')
            exec ("fig.add_trace(go.Bar(name=i,x=x,y=%s))" % (listname))


app.layout = html.Div(children=[
    html.H1(children='Werkvoorraad Bedrijfsbureau'),

    html.Div(children='''
        Tijdlijn per lijst (niet Done)
    '''),

    dcc.Graph(figure=fig),
    html.Div(children='''
        Another timeline (just a copy for now)
    '''),
    dcc.Graph(figure=fig)
])
if __name__ == '__main__':
    app.run_server(debug=True,host='0.0.0.0')
