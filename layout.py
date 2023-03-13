from dash import Dash, dcc, html, Input, Output, State
import visualisation

app = Dash('SER-TS')

map_start = visualisation.create_map(visualisation.df_map)
stats_plot_all = visualisation.stats_n_plots(visualisation.df_map, 2023, [], [])

# create a dict of all the years with new LNG terminals to use for the slider
marks_dict = {int(year): {"label": str(year), "style": {"transform": "rotate(45deg)"}}
              for year in visualisation.df_map['start up date'].unique()}

# list of options for country filter
country_selection = visualisation.df_map['country'].sort_values().unique().tolist()
type_selection = visualisation.df_map['type'].unique().tolist()

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
        dcc.Slider(min(marks_dict.keys()), 2030, step=None,
                   marks=marks_dict,
                   id='years_slider',
                   value=2023
                   ),

        # interactive map
        dcc.Graph(
            id='map',
            figure=map_start
        )]
    ),

    # additional stats
    html.Div([
        # header
        html.H2('Overall annual capacity'),

        # filters
        # todo put filters next to each other
        html.Div([
            # dropdown for country and type
            html.Div([dcc.Dropdown(
                options=country_selection,
                multi=True,
                id='country_slct')],
            ),
            html.Div([dcc.Dropdown(
                options=type_selection,
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
            figure=stats_plot_all
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
    filtered_map = visualisation.create_map(df)

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

    return fig
