from dash import Dash, dcc, html, Input, Output, State
import data


app = Dash('SER-TS')

# create a dict of all the years with new LNG terminals to use for the slider
marks_dict = {int(year): {"label": str(year), "style": {"transform": "rotate(45deg)"}}
              for year in data.df_lng_terminals[data.START_UP_DATE].unique()}

# list of options for filters
country_selection = ['Europe'] + data.df_lng_terminals[data.COUNTRY].sort_values().unique().tolist()
type_selection = data.df_lng_terminals[data.TYPE].unique().tolist()
country_selection_demand = ['Europe'] + data.df_demand_2021[data.COUNTRY].sort_values().unique().tolist()

app.layout = html.Div(children=[
    # header and background info
    html.Div([
        html.H1(children='Overview of european LNG terminals until 2030'),

        html.Div(children=[html.P(children='''The russian war against Ukraine is affecting the european security 
                                                            of supply regarding methane. An essential part to ensure the 
                                                            gas supply in Europe are LNG terminals.'''
                                  ),
                           html.P(children='Task: Mapping european LNG terminals including operating data'),
                           html.P(children=['Source: ',
                                            html.A('GIE', href='https://www.gie.eu/publications/maps/gie-lng-map/')]
                                  )
                           ]
                 ), ]
             ),

    # main body: map and filter (slider)
    html.Div([
        # Slider to filter for terminals up to a certain year
        dcc.Slider(min(marks_dict.keys()), 2031, step=None,
                   marks=marks_dict,
                   id='years_slider',
                   value=2023
                   ),

        # interactive map
        dcc.Graph(
            id='map'
        )]
    ),

    # additional stats
    html.Div([
        # header
        html.H2('Overall annual capacity'),

        # filters
        html.Div([
            # dropdown for country and type
            html.Div([dcc.Dropdown(
                options=country_selection,
                placeholder='all countries',
                multi=True,
                id='country_slct')],
            ),
            html.Div([dcc.Dropdown(
                options=type_selection,
                placeholder='all types',
                multi=True,
                id='type_slct')],
            ),

            # entry box for year
            html.Div([dcc.Input(
                id="input_year",
                type='number',
                value='2023',)]
            ),

            html.Button('Submit', id='submit_filter', n_clicks=0),

        ], style={'width': '15%'}
        ),

        # Plot
        html.Div([dcc.Graph(
            id='stats_plot'
        )]),


        # header
        html.H2('Capacity and Demand'),

        # filters
        html.Div([
            # dropdown for country and type
            html.Div([dcc.Dropdown(
                options=country_selection_demand,
                multi=True,
                placeholder='all countries',
                id='country_slct_demand')],
            ),

            # entry box for year
            html.Div([dcc.Input(
                id="input_year_demand",
                type='number',
                value='2023', )]
            ),

            html.Button('Submit', id='submit_filter_demand', n_clicks=0),

        ], style={'width': '15%'}
        ),

        # Plot
        html.Div([dcc.Graph(
            id='demand_plot'
        )])

    ])

])


@app.callback(
    Output('map', 'figure'),
    Input('years_slider', 'value')
)
def update_map(year_slct):
    # create map
    filtered_map = data.create_map(data.df_lng_terminals, year_slct)

    return filtered_map


@app.callback(
    Output('stats_plot', 'figure'),
    Input('submit_filter', 'n_clicks'),
    [State('input_year', 'value'),
     State('country_slct', 'value'),
     State('type_slct', 'value')]
)
def update_terminals_stats(submit_btn, year_slct, country_slct, type_slct):
    # if intially no input is selected, the state defaults to None
    # if all selections are removed it returns an empty list
    # create uniform behaviour for the plotting functions
    country_slct = country_slct if country_slct else None
    type_slct = type_slct if type_slct else None
    year_slct = 2023 if year_slct is None else int(year_slct)

    fig = data.plot_terminal_capacities(data.df_lng_terminals, year_slct, country_slct, type_slct)

    return fig


@app.callback(
    Output('demand_plot', 'figure'),
    Input('submit_filter_demand', 'n_clicks'),
    [State('input_year_demand', 'value'),
     State('country_slct_demand', 'value')]
)
def update_demand_stats(submit_btn, year_slct, country_slct):
    # if intially no input is selected, the state defaults to None
    # if all selections are removed it returns an empty list
    # create uniform behaviour for the plotting functions
    country_slct = country_slct if country_slct else None
    year_slct = 2023 if year_slct is None else int(year_slct)

    fig = data.plot_demand(data.df_lng_terminals, data.df_demand_2021, year_slct, country_slct)

    return fig
