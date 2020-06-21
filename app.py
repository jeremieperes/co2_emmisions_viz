# -*- coding: utf-8 -*-

import os
from random import randint

import numpy as np
import pandas as pd
import requests
import plotly.express as px

import pycountry_convert as pc

import plotly.express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output


# Load and clean data
data_folder = 'data/'

def clean_csv(dataframe, indicator):
    df = dataframe.copy()
    df.drop(columns=['Indicator Name', 'Indicator Code', 'Country Name'], inplace=True)
    df.dropna(axis=1, inplace=True, how='all')
    df = df.T
    df.columns = df.iloc[0].values
    df.drop(axis=0, index='Country Code', inplace=True)
    #df['WORLD'] = df.sum(axis=1)
    df.reset_index(inplace=True)
    df.rename(columns={'index':'year'}, inplace=True)
    df = df.melt(id_vars=['year'], value_vars=df.drop(columns='year').columns, var_name='country', value_name=indicator)
    df.year = df.year.astype(int)
    return df

df1 = pd.read_csv(data_folder+"CO2.csv", skiprows=4)
df2 = pd.read_csv(data_folder+"electric_power_consumption.csv", skiprows=4)
df3 = pd.read_csv(data_folder+"CO2_tot.csv", skiprows=4)
df4 = pd.read_csv(data_folder+"access_electricity.csv", skiprows=4)
df5 = pd.read_csv(data_folder+"energy_used.csv", skiprows=4)
df6 = pd.read_csv(data_folder+"forest_area.csv", skiprows=4)
df7 = pd.read_csv(data_folder+"gdp.csv", skiprows=4)
df8 = pd.read_csv(data_folder+"population.csv", skiprows=4)
df9 = pd.read_csv(data_folder+"renewable_energy_consumption.csv", skiprows=4)
df10 = pd.read_csv(data_folder+"urban_population.csv", skiprows=4)


co2 = clean_csv(df1, indicator='co2_per_capita')
electric_power_consumption = clean_csv(df2, indicator='electric_power_consumption')
co2_tot = clean_csv(df3, indicator='co2_total')

access_electricity = clean_csv(df4, indicator='access_to_electricity')
energy_used = clean_csv(df5, indicator='energy_used')
forest_area = clean_csv(df6, indicator='forest_area')
gdp = clean_csv(df7, indicator='gdp')
population = clean_csv(df8, indicator='population')
renewable_energy_consumption = clean_csv(df9, indicator='renewable_energy_consumption')
urban_population = clean_csv(df10, indicator='urban_population')

df = co2.copy()
corres_country = df1[['Country Name', 'Country Code']]

df['co2_total'] = co2_tot.co2_total
df['electric_power_consumption'] = electric_power_consumption.electric_power_consumption
df['access_to_electricity'] = access_electricity.access_to_electricity
df['energy_used'] = energy_used.energy_used
df['forest_area'] = forest_area.forest_area
df['gdp'] = gdp.gdp
df['population'] = population.population
df['renewable_energy_consumption'] = renewable_energy_consumption.renewable_energy_consumption
df['urban_population'] = urban_population.urban_population


df = pd.merge(corres_country, df, right_on='country', left_on='Country Code')
df.drop(columns='country', inplace=True)
df.rename(columns={'Country Name':'country_name', 'Country Code':'country_code'}, inplace=True)

res = []
for row in range (df.shape[0]) :
    try :
        res.append(pc.convert_continent_code_to_continent_name(pc.country_alpha2_to_continent_code(pc.country_name_to_country_alpha2(df["country_name"][row]))))
    except :
        res.append(df["country_name"][row])

df["continent"] = res

# Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server


country_options = [
    {"label": country_name, "value": country_name}
    for country_name in df.country_name.unique()
]

year_options = [
    {"label": year, "value": year}
    for year in df.year.unique()
]

def filter_dataframe(df, selected_countries, selected_years):

    if type(selected_countries)==str:
        selected_countries = [selected_countries]
    elif not selected_countries:
        selected_countries = df["country_name"].unique()

    dff = df[
        df["country_name"].isin(selected_countries)
        & (df["year"] > selected_years[0])
        & (df["year"] < selected_years[1])
    ]
    return dff

def filter_dataframe_2(df, selected_countries, selected_year):

    if type(selected_countries)==str:
        selected_countries = [selected_countries]
    elif not selected_countries:
        selected_countries = df["country_name"].unique()

    dff = df[
        df["country_name"].isin(selected_countries)
        & (df["year"] == selected_year)]
    return dff


app.layout = html.Div(
    [
        dcc.Store(id="aggregate_data"),
        # empty Div to trigger javascript file for graph resizing
        html.Div(id="output-clientside"),
        html.Div(
            [
                html.Div(
                    [
                        html.Img(
                            src=app.get_asset_url("CO2.png"),
                            id="CO2-image",
                            style={
                                "height": "60px",
                                "width": "auto",
                                "margin-bottom": "25px",
                            },
                        )
                    ],
                    className="one-third column",
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "CO2 emissions in the world",
                                    style={"margin-bottom": "0px"},
                                ),
                                html.H5(
                                    "A recent overview", style={"margin-top": "0px"}
                                ),
                            ]
                        )
                    ],
                    className="one-half column",
                    id="title",
                ),
                html.Div(
                    [
                        html.A(
                            html.Button("Learn More", id="learn-more-button"),
                            href="https://leclimatchange.fr/",
                        )
                    ],
                    className="one-third column",
                    id="button",
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),
        dcc.Tabs(id="tabs", value='emission', children=[
                            dcc.Tab(label='Global emission of CO2', value='emission'),
                            dcc.Tab(label='Correlation of emission and human activity', value='correlation'),
                    ]),
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            "Filter by date (or select range in histogram):",
                            className="control_label",
                        ),
                        dcc.RangeSlider(
                            id="year_slider",
                            min=1960,
                            max=2014,
                            value=[1960, 2014],
                            className="dcc_control",
                        ),
                        html.P("Filter by country:", className="control_label"),
                        dcc.Dropdown(
                            id="country_selector",
                            options=country_options,
                            value=[],
                            multi=True,
                            className="dcc_control",
                        ),
                        html.P("Choose a metric for CO2 emission:", className="control_label"),
                        dcc.RadioItems(
                            id="metric_selector",
                            options=[
                                {"label": "Metric tons per capita ", "value": "co2_per_capita"},
                                {"label": "Kilo tons ", "value": "co2_total"},
                            ],
                            value="co2_per_capita",
                            labelStyle={"display": "inline-block"},
                            className="dcc_control",
                        ),
                        html.P("Choose a metric to compare with CO2 emissions:", className="control_label", id="metric_title", style = dict(display='none')),
                        dcc.RadioItems(
                            id="metric",
                            options=[
                                {"label": "Electric power consumption (kWh per capita)", "value": "electric_power_consumption"},
                                {"label": "Access to electricity (% of population)", "value": "access_to_electricity"},
                                {"label": "Energy use (kg of oil equivalent per capita)", "value": "energy_used"},
                                {"label": "Forest area (% of land area)", "value": "forest_area"},
                                {"label": "GDP per capita (current US$)", "value": "gdp"},
                                {"label": "Population", "value": "population"},
                                {"label": "Renewable energy consumption (% of total final energy consumption)", "value": "renewable_energy_consumption"},
                                {"label": "Urban population (% of total population)", "value": "urban_population"}

                            ],
                            value="electric_power_consumption",
                            labelStyle={"display": "none"},
                            className="dcc_control",
                        )
                    ],
                    className="pretty_container four columns",
                    id="cross-filter-options",
                ),

                html.Div(
                    id="right-column",
                    className="eight columns",
                ),
            ],
            className="row flex-display",
        )
    ],
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},
)


# Define callback to update graph


@app.callback(Output('right-column', 'children'),
              [Input('tabs', 'value')])
def render_content(tab_value):
    if tab_value == 'emission':
        return [html.Div(
                            [
                                html.Div(
                                    [html.H6(id="co2_total_text"), html.P("Mean of CO2 emissions (kt)")],
                                    id="co2_total",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [html.H6(id="co2_per_capita_text"), html.P("Mean of CO2 emissions (metric tons per capita)")],
                                    id="co2_per_capita",
                                    className="mini_container",
                                )
                            ],
                            id="info-container",
                            className="row container-display",
                        ),
                        html.Div(
                            [dcc.Graph(id="graph1")],
                            id="countGraphContainer1",
                            className="pretty_container",
                        ),
                        html.Div(
                            [dcc.Graph(id="graph2")],
                            id="countGraphContainer2",
                            className="pretty_container",
                        ),
                        html.Div(
                            [dcc.Graph(id="graph3")],
                            id="countGraphContainer3",
                            className="pretty_container",
                        )]

    elif tab_value == 'correlation':
        return html.Div(
                            [dcc.Graph(id="graph4")],
                            id="countGraphContainer4",
                            className="pretty_container",
                        )



@app.callback(
    [Output('metric', 'labelStyle'),
    Output('metric_title', 'style')],
    [Input('tabs', 'value')]
)
def update_tabs_option(tab_value) :
    if (tab_value == "emission") :
        return {'display' : 'none'},  dict(display='none')
    else :
        return {'display' : 'inline-block'}, dict()


@app.callback(
    [
        Output("co2_total_text", "children"),
        Output("co2_per_capita_text", "children"),
        Output("co2_total","style"),
        Output("co2_per_capita","style")
    ],
    [Input('country_selector', 'value'),
    Input('year_slider', 'value'),
    Input('tabs', 'value')],
)
def update_text(selected_countries, selected_years, tab_value):
    dff = filter_dataframe(df, selected_countries, selected_years)

    return round(dff.co2_total.mean(),2) , round(dff.co2_per_capita.mean(),2) , dict(), dict()


@app.callback(
    Output('graph1', 'figure'),
    [Input('country_selector', 'value'),
    Input('year_slider', 'value'),
    Input('metric_selector', 'value'),
    ]
)
def update_graph1(selected_countries, selected_years, selected_metric):

    dff = filter_dataframe(df, selected_countries, selected_years)
    fig = px.line(dff, x='year', y=selected_metric, color='country_name',
                  title='Evolution of the CO2 emissions accross the years')
    fig.update_xaxes(rangeslider_visible=True)
    return fig



@app.callback(
    Output('graph2', 'figure'),
    [Input('country_selector', 'value'),
    Input('year_slider', 'value'),
    Input('metric_selector', 'value')]
)
def update_graph2(selected_countries, selected_years, selected_metric):

    dff = filter_dataframe(df, selected_countries, selected_years)

    fig = px.choropleth(dff, locations="country_code", color=selected_metric, hover_name="country_name",
                        animation_frame="year", range_color=[0,20], title='World map of CO2 emissions', color_continuous_scale=px.colors.diverging.RdYlGn[::-1])

    return fig


@app.callback(
    Output('graph3', 'figure'),
    [Input('country_selector', 'value'),
    Input('year_slider', 'value'),
    Input('metric_selector', 'value')]
)
def update_graph3(selected_countries, selected_years, selected_metric):

    dff = filter_dataframe(df, selected_countries, selected_years)
    fig = px.bar(dff, x='country_name', y=selected_metric, color='continent',
                  title='Comparaison of CO2 emissions per year', animation_frame="year")
    return fig


@app.callback(
    Output('graph4', 'figure'),
    [Input('country_selector', 'value'),
    Input('year_slider', 'value'),
    Input('metric_selector', 'value'),
    Input('metric', 'value'),
    ]
)
def update_graph4(selected_countries, selected_years, c02_selected_metric, other_metric):

    dff = filter_dataframe(df, selected_countries, selected_years)

    fig = px.scatter(dff, x=other_metric, y=c02_selected_metric, color='continent', animation_frame="year", hover_name="country_name",
                  title='Correlation between CO2 emissions and othe metric')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
