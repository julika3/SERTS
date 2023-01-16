from dash import Dash, dcc, html, Input, Output
import visualisation

app = Dash('SER-TS')

fig = visualisation.create_map(visualisation.df_map)
marks_dict = {int(year): {"label": str(year), "style": {"transform": "rotate(45deg)"}}
                for year in visualisation.df_map['start up date'].unique()}

app.layout = html.Div(children=[
                html.H1(children='Overview of european LNG terminals until 2030'),

                html.Div(children=[html.P(children='''The russian war against Ukraine is affecting the european security 
                                                        of supply regarding methane. An essential part to ensure the gas
                                                         supply in Europe are LNG terminals.'''),
                                   html.P(children='Task: Mapping european LNG terminals including operating data'),
                                   html.P(children=['Source: ',
                                                    html.A('GIE', href='https://www.gie.eu/publications/maps/gie-lng-map/')
                                                    ]
                                          )
                                   ]
                         ),

                dcc.Slider(min(marks_dict.keys()), 2030, step=None,
                           marks=marks_dict,
                           id='years_slider',
                           value=2023
                           ),

                dcc.Graph(
                    id='map',
                    figure=fig
                )
            ])
