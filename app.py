import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import numpy as np

# data proprocess
data=pd.read_csv("votings.csv")
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
        go.Bar(name='adopted', x=tdist.index, y=tdist['adopted'],marker_color='#87CE70'),
        go.Bar(name='rejected', x=tdist.index, y=-tdist['rejected'],marker_color='#FFCC80')
    ],
    layout=go.Layout(
        title=dict(text='topic distribution',x=0.5),
        xaxis=dict(),
        yaxis=dict(title='number of motions',gridcolor='#EEEEEE',zerolinecolor='#EEEEEE',tickformat='d'),
        bargap=0.5,
        barmode='stack',
        plot_bgcolor='#FFFFFF'
    )
)

#plot fig2
support=data.groupby('topic')[parties].sum().reset_index()
support.insert(0,"decision",np.full(len(topics), "support"))
against=data.groupby('topic')[parties].agg(lambda x: x.eq(0).sum()).reset_index()
against.insert(0,"decision",np.full(len(topics), "against"))
patti=pd.concat([support,against]).set_index(['topic','decision'])

fig2_dic={}
for t in topics:
    fig2_dic[t]=go.Figure(
        data=[
            go.Bar(y=patti.columns, x=patti.loc[t,'support'], name='in front of', orientation='h',marker_color='#A6C4FE'),
            go.Bar(y=patti.columns, x=patti.loc[t,'against'], name='against', orientation='h',marker_color='#DDDDDD')],
        layout=go.Layout(
            title=dict(text='voting result regarding '+ str(t)+' topic',x=0.5),
            xaxis=dict(title='number of motions',tickformat='d'),
            yaxis=dict(),
            bargap=0.5,
            barmode='stack',
            plot_bgcolor='#FFFFFF'
        )
    )

# plot fig3
propose=data[['proposer','topic']]
propose.insert(2, "value", np.ones(nmotions), True) 
propose=propose.groupby(['proposer','topic']).sum().reset_index()
propose=propose.pivot(index='proposer', columns='topic',values='value').fillna(0)

trace=[]
for i in propose.index:
    trace.append(go.Scatterpolar(r=propose.loc[i], theta=propose.columns, fill='toself', name=i))
fig3=go.Figure(
    data=trace,
    layout=go.Layout(
        title=dict(text='topic distribution of motions proposed by different parties',x=0.5),
        polar=dict(radialaxis=dict(gridcolor='#EEEEEE',tickformat='d'),bgcolor='#FFFFFF')
    )
)

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__)

# html
app.layout = html.Div(children=[
    html.H1(children='Hello Dash',
            style={'width':'100%','height':50,'font-size': 20,'marginTop':0}),

    html.Div([
        dcc.Graph(id='fig1',figure=fig1)],
        style={'wide':'80%','height':400,'textAlign': 'center','marginLeft':30,'marginRight':30,'marginBottom':'10','border':'2px'}),

    html.Div([
        dcc.Dropdown(
            id='fig2_dropdown',
            options=[{'label':i, 'value':i} for i in topics],
            value='Health'),
    
        dcc.Graph(id='fig2')],
        style={'width':'47%','marginTop':80,'marginLeft':30,'border':2,'display':'inline-block','vertical-align':'top'}),
   
    html.Div([
        dcc.Graph(id='fig3',figure = fig3)],
        style={'width': '47%','marginTop':80,'marginLeft':30,'border':2,'display': 'inline-block','vertical-align':'top'}),
],   
    style={'backgroundColor':'#F6F6F6'})

@app.callback(
    Output('fig2','figure'),
    [Input('fig2_dropdown','value')])

def update_graph(t):
    return fig2_dic[t]


if __name__ == '__main__':
    app.run_server(debug=True, host='192.168.1.101', port = 8090)