# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html

import pandas as pd

import plotly.graph_objects as go
import plotly.express as px


# Load and clean data
df = pd.read_csv("CO2.csv", skiprows=4)
df.drop(columns=['Indicator Name', 'Indicator Code', 'Country Name'], inplace=True)
df.dropna(axis=1, inplace=True, how='all')
df = df.T
df.columns = df.iloc[0].values
df.drop(axis=0, index='Country Code', inplace=True)
#df['WORLD'] = df.sum(axis=1)
df.reset_index(inplace=True)
df.rename(columns={'index':'year'}, inplace=True)
df = df.melt(id_vars=['year'], value_vars=df.drop(columns='year').columns, var_name='country', value_name='co2')

# Dash app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

fig = px.line(df, x='year', y='co2', color='country')

app.layout = html.Div(children=[
    html.H1(children='Evolution of CO2 emmisions'),

    html.Div(children='''
        A MS Big Data Project for IGR204 course
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])


if __name__ == '__main__':
    app.run_server(debug=True, port=8000, host='127.0.0.1')
