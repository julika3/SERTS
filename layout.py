from dash import Dash, dcc, html, Input, Output, State
import visualisation

app = Dash('SER-TS')

stats_plot_start = visualisation.stats_n_plots(visualisation.df_map, 2023,
                                               visualisation.df_map['country'].sort_values().unique().tolist(), [])

# create a dict of all the years with new LNG terminals to use for the slider
marks_dict = {int(year): {"label": str(year), "style": {"transform": "rotate(45deg)"}}
              for year in visualisation.df_map['start up date'].unique()}

# list of options for filters
country_selection = ['Europe'] + visualisation.df_map['country'].sort_values().unique().tolist()
type_selection = visualisation.df_map['type'].unique().tolist()
country_selection_demand = ['Europe'] + visualisation.df_demand['country'].sort_values().unique().tolist()

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
            id='stats_plot',
            figure=stats_plot_start
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
def filter_map(year_slct):
    # filter dataframe for terminals build before or in selected year
    df = visualisation.df_map[visualisation.df_map['start up date'] <= year_slct]

    # aggregate facilities and their expansions
    df_agg = df.groupby(['latitude', 'longitude', 'type']).first()
    df_agg['annual capacity'] = df.groupby(['latitude', 'longitude', 'type'])['annual capacity'].sum()
    df_agg['min capacity [kWh]'] = df.groupby(['latitude', 'longitude', 'type'])['min capacity [kWh]'].sum()
    df_agg['max capacity [kWh]'] = df.groupby(['latitude', 'longitude', 'type'])['max capacity [kWh]'].sum()
    df_agg['latitude'], df_agg['longitude'], df_agg['type'] = zip(*df_agg.index)
    df_agg.reset_index(drop=True, inplace=True)

    # create map
    filtered_map = visualisation.create_map(df_agg)

    return filtered_map


@app.callback(
    Output('stats_plot', 'figure'),
    Input('submit_filter', 'n_clicks'),
    [State('input_year', 'value'),
     State('country_slct', 'value'),
     State('type_slct', 'value')]
)
def update_stats(submit_btn, year_slct, country_slct, type_slct):
    country_slct = [] if country_slct is None else country_slct
    type_slct = [] if type_slct is None else type_slct
    year_slct = 2023 if year_slct is None else int(year_slct)

    fig = visualisation.stats_n_plots(visualisation.df_map, year_slct, country_slct, type_slct)
    #fig = visualisation.plot_demand(visualisation.df_map, visualisation.df_demand, country_slct[0], year_slct)

    return fig


@app.callback(
    Output('demand_plot', 'figure'),
    Input('submit_filter_demand', 'n_clicks'),
    [State('input_year_demand', 'value'),
     State('country_slct_demand', 'value')]
)
def update_stats(submit_btn, year_slct, country_slct):
    country_slct = [] if country_slct is None else country_slct
    year_slct = 2023 if year_slct is None else int(year_slct)

    fig = visualisation.plot_demand(visualisation.df_map, visualisation.df_demand, country_slct, year_slct)

    return fig
