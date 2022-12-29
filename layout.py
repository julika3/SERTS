from dash import Dash, dcc, html, Input, Output
import visualisation

app = Dash('SER-TS')

fig = visualisation.create_map(visualisation.df_map)

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

                dcc.Graph(
                    id='map',
                    figure=fig
                )
            ])
