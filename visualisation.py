import plotly.graph_objects as go
import pandas as pd

# prepare the dataframe vor visualisation
# todo make function
df_map = pd.read_excel('database.xlsx', skiprows=0)
df_map['annual capacity'] = df_map['annual capacity'].map(lambda x: 0 if x == '?' else float(x))
df_map['latitude'] = df_map['latitude'].map(lambda x: float(x))
df_map['longitude'] = df_map['longitude'].map(lambda x: float(x))
df_map['description'] = 'Location: ' + df_map['location'] \
                        + '<br>Type: ' + df_map['type'] \
                        + '<br>Start up Date: ' + df_map['start up date'].astype(str) \
                        + '<br>Annual Capacity: ' + df_map['annual capacity'].map(lambda x: x / 10**9).astype(str) \
                        + ' billion m<sup>3</sup>'


def create_map(df):
    fig = go.Figure()

    fig.update_layout(
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
            lonaxis_range=[df['longitude'].min() - 5, df['longitude'].max() + 5],
            lataxis_range=[df['latitude'].min() - 5, df['latitude'].max() + 5],
        ),

        legend_traceorder='reversed'
    )

    # bubble_sizes = df['annual capacity'] / df['annual capacity'].max()

    type_clr_dct = {'onshore facility': 'red', 'FSRU': 'blue', 'offshore facility': 'darkblue', 'expansion 1': 'green',
                    'expansion 2': 'green', 'other': 'black'}
    df['type'] = df['type'].map(lambda x: x if x in type_clr_dct.keys() else 'other')


    # add the terminals to the map via their latitude and longitude coordinates
    fig.add_trace(go.Scattergeo(
        lon=df['longitude'],
        lat=df['latitude'],
        text=df['description'],
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

    fig.update_layout(
        height=1200,
    )

    return fig

# fig.show()
