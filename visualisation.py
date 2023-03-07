import plotly.graph_objects as go
import pandas as pd


def read_terminals_csv():
    global df_map
    # prepare the dataframe vor visualisation
    df_map = pd.read_excel('database.xlsx', skiprows=0)
    df_map['annual capacity'] = df_map['annual capacity'].map(lambda x: 0 if x == '?' else float(x))
    df_map['latitude'] = df_map['latitude'].map(lambda x: float(x))
    df_map['longitude'] = df_map['longitude'].map(lambda x: float(x))
    # description to be displayed in as hover text (html formatting)
    df_map['description'] = 'Location: ' + df_map['location'] \
                            + '<br>Type: ' + df_map['type'] \
                            + '<br>Start up Date: ' + df_map['start up date'].astype(str) \
                            + '<br>Annual Capacity: ' + df_map['annual capacity'].map(lambda x: x / 10 ** 9).astype(str) \
                            + ' billion m<sup>3</sup>'
    # todo improve default value / research dates
    df_map['start up date'] = df_map['start up date'].map(lambda x: 2000 if x == '?' else x)

    return df_map


def create_map(df):
    fig = go.Figure()

    fig.update_layout(
        title='LNG Terminals in Europe',
        title_x=0.5,
        showlegend=True,
        legend_title='Facility Type',
        geo=go.layout.Geo(
            resolution=50,
            scope='world',
            showframe=True,
            framecolor='black',
            showcoastlines=True, coastlinecolor="darkgrey",
            landcolor="rgb(229, 229, 229)",
            showcountries=True, countrycolor="darkgrey",
            showocean=True, oceancolor="LightBlue",
            showlakes=False,
            projection_type='mercator',
            lonaxis_range=[df['longitude'].min() - 5, df['longitude'].max() + 5],
            lataxis_range=[df['latitude'].min() - 1, df['latitude'].max() + 5],
        ),
    )

    # bubble_sizes = df['annual capacity'] / df['annual capacity'].max()

    # add the terminals to the map via their latitude and longitude coordinates
    for trmnl_type in df['type'].unique().tolist():
        df_plot = df[df['type'] == trmnl_type]
        fig.add_trace(go.Scattergeo(
            name=trmnl_type,
            lon=df_plot['longitude'],
            lat=df_plot['latitude'],
            text=df_plot['description'],
            marker=dict(
                # scale the bubbles according to their relative annual capacity
                size=df_plot['annual capacity'] / df_plot['annual capacity'].max() * 200,
                opacity=0.6,
                line_color='black',
                line_width=0.6,
                sizemode='area'
            )
        ))

    fig.update_layout(
        height=1200,
    )

    return fig


df_map = read_terminals_csv()
