import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import urllib.request as request

# data proprocess
r = request.urlopen("https://raw.githubusercontent.com/founting/votes/master/votings.csv")
data=pd.read_csv(r)
topics=np.unique(data['topic'].values)
parties=np.array(data.columns[5:20])

nmotions=data.shape[0]

#plot fig1
tdist=data[['topic','decision']]
tdist.insert(1, "total", np.ones(nmotions), True) 
tdist=tdist.groupby('topic')['total','decision'].sum()
tdist=tdist.rename(columns={'decision':'adopted'})
tdist.insert(2, "rejected", tdist['total']-tdist['adopted'], True)

fig1=go.Figure(
    data=[
        go.Bar(name='adopted', x=tdist.index, y=tdist['adopted'],base=0,marker_color='#87CE70'),
        go.Bar(name='rejected', x=tdist.index, y=-tdist['rejected'],base=0,marker_color='#FFCC80')
    ],
    layout=go.Layout(
        title=dict(text='Topic distribution',x=0.5),
        xaxis=dict(),
        yaxis=dict(title='number of motions',gridcolor='#EEEEEE',zerolinecolor='#EEEEEE',tickformat='d'),
        bargap=0.5,
        barmode='stack',
        plot_bgcolor='#FFFFFF'
    )
)

# plot fig2
corr = data.iloc[:,5:].corr()
corr = corr.fillna(1)
fig2 = go.Figure(
    data = (
        go.Heatmap(
        zmin=-1,
        zmax=1,
        z=corr,
        x= parties,
        y = parties,
        colorscale='tealrose'
        )
    ),
    layout = go.Layout(
        title=dict(text = 'Correlation analysis between parties',x=0.5),
    )
)

#plot fig3
support=data.groupby('topic')[parties].sum().reset_index()
support.insert(0,"decision",np.full(len(topics), "support"))
against=data.groupby('topic')[parties].agg(lambda x: x.eq(0).sum()).reset_index()
against.insert(0,"decision",np.full(len(topics), "against"))
patti=pd.concat([support,against]).set_index(['topic','decision'])

fig3_dic={}
for t in topics:
    fig3_dic[t]=go.Figure(
        data=[
            go.Bar(y=patti.columns, x=patti.loc[t,'support'], name='in front of', orientation='h',marker_color='#A6C4FE'),
            go.Bar(y=patti.columns, x=patti.loc[t,'against'], name='against', orientation='h',marker_color='#DDDDDD')],
        layout=go.Layout(
            title=dict(text='Voting result regarding '+ str(t)+' topic',x=0.5),
            xaxis=dict(title='number of motions',tickformat='d'),
            yaxis=dict(),
            bargap=0.5,
            barmode='stack',
            plot_bgcolor='#FFFFFF',
            height=450
        )
    )

# plot fig4
propose=data[['proposer','topic']]
propose.insert(2, "value", np.ones(nmotions), True) 
propose=propose.groupby(['proposer','topic']).sum().reset_index()
propose=propose.pivot(index='proposer', columns='topic',values='value').fillna(0)

trace=[]
for p in propose.index:
    trace.append(go.Scatterpolar(r=propose.loc[p], theta=propose.columns, fill='toself', name=p))
fig4=go.Figure(
    data=trace,
    layout=go.Layout(
        title=dict(text='Topic distribution of motions proposed by various parties',x=0.5),
        polar=dict(radialaxis=dict(range=[0,2.1],gridcolor='#C6C6C6',tickformat='d'),
                    angularaxis=dict(gridcolor='#C6C6C6'),bgcolor='#FFFFFF'),
        height=487
))

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__,external_stylesheets=external_stylesheets)
server=app.server

# html
app.layout = html.Div(children=[
    html.H1(children='Votes inside the Dutch Parliament',
            style={'width':'99%','height':30,'fontSize': 20,'color':'#FFFFFF',
            'paddingLeft':18,'paddingTop':5,'backgroundColor':'#363880'}),

    html.Div([
        dcc.Graph(id='fig1',figure=fig1)],
        style={'width':'47%','marginTop':10,'marginLeft':30,'border':'2px','display':'inline-block','vertical-align':'top'}),
    
    html.Div([
        dcc.Graph(id='fig2', figure=fig2)],
        style={'width':'47%','marginTop':10,'marginLeft':20, 'marginRight':30,'border': '2px','display':'inline-block','vertical-align':'top'}),

    html.Div([
        dcc.Dropdown(
            id='fig3_dropdown',
            options=[{'label':i, 'value':i} for i in topics],
            value='Housing',
            style={'height':37}),
        dcc.Graph(id='fig3')],
        style={'width':'47%','marginTop':25,'marginBottom':25,'marginLeft':30,'border':2,'display':'inline-block','vertical-align':'top'}),
   
    html.Div([
        dcc.Graph(id='fig4',figure = fig4)],
        style={'width': '47%','marginTop':25,'marginBottom':25,'marginLeft':20,'marginRight':30,'border':2,'display': 'inline-block','vertical-align':'top'}),
],   
    style={'backgroundColor':'#F6F6F6'})

@app.callback(
    Output('fig3','figure'),
    [Input('fig3_dropdown','value')])

def update_graph(t):
    return fig3_dic[t]


if __name__ == '__main__':
    app.run_server()