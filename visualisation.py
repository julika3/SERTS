import plotly.graph_objects as go
import pandas as pd
import dash

app = dash.Dash('SERTS')

df = pd.read_excel('database.xlsx', skiprows=0)
df['annual capacity'] = df['annual capacity'].map(lambda x: 0 if x == '?' else float(x))

fig = go.Figure()

# fig['data'][0].update(mode='markers+text', textposition='bottom center',
#                       text=df['annual capacity'].map('{:.0f}'.format).astype(str) + ' ' + \
#                            df['country'])

fig.update_layout(
    title=go.layout.Title(
        text='LNG Terminals in Europe until 2030<br> \
                Source: <a href="https://www.gie.eu/publications/maps/gie-lng-map/">\
                GIE</a>'),
    geo=go.layout.Geo(
        resolution=50,
        scope='europe',
        showframe=True,
        framecolor='black',
        showcoastlines=True,
        landcolor="rgb(229, 229, 229)",
        countrycolor="darkgrey",
        coastlinecolor="darkgrey",
        projection_type='mercator',
    ),

    legend_traceorder='reversed'
)

# bubble_sizes = df['annual capacity'] / df['annual capacity'].max()

type_clr_dct = {'onshore facility': 'red', 'FSRU': 'blue', 'offshore facility': 'darkblue', 'expansion 1': 'green',
                'expansion 2': 'green', 'other': 'black'}
df['type'] = df['type'].map(lambda x: x if x in type_clr_dct.keys() else 'other')


# add the terminals to the map via their latitude and longitude coordinates
fig.add_trace(go.Scattergeo(
    #locationmode='USA-states',
    lon=df['longitude'],
    lat=df['latitude'],
    text=df['location'],
    marker=dict(
        # scale the bubbles according to their relative annual capacity
        size=df['annual capacity'] / df['annual capacity'].max() * 200,
        # colour bubbles according to set dictionary
        color=df['type'].map(type_clr_dct),
        line_color='black',
        line_width=0.5,
        sizemode='area'
    )
))

fig.show()
