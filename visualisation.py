import plotly.graph_objects as go
import pandas as pd


type_colour_dict = {'FRU + direct link to UGS': 'darkblue',
                    'FSRU': 'cornflowerblue',
                    'FSU and onshore Regasification': 'seagreen',
                    'offshore GBS': 'slateblue',
                    'onshore facility': 'olive'
                    }


def read_terminals_db():
    # prepare the dataframe vor visualisation
    df_db = pd.read_excel('database.xlsx', skiprows=0)
    df_db['annual capacity'] = df_db['annual capacity'].map(lambda x: 0 if x == '?' else float(x))
    df_db['latitude'] = df_db['latitude'].map(lambda x: float(x))
    df_db['longitude'] = df_db['longitude'].map(lambda x: float(x))
    # description to be displayed in as hover text (html formatting)
    df_db['description'] = 'Location: ' + df_db['location'] \
                            + '<br>Type: ' + df_db['type'] \
                            + '<br>Start up Date: ' + df_db['start up date'].astype(str) \
                            + '<br>Annual Capacity: ' + df_db['annual capacity'].map(lambda x: x / 10 ** 9).astype(str) \
                            + ' billion m<sup>3</sup>'
    # todo improve default value / research dates
    df_db['start up date'] = df_db['start up date'].map(lambda x: 2030 if x == '?' else x)

    return df_db


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
            lonaxis_range=[df['longitude'].min() - 3, df['longitude'].max() + 3],
            lataxis_range=[df['latitude'].min() - 1, df['latitude'].max() + 3],
        ),
    )

    # add the terminals to the map via their latitude and longitude coordinates
    for trmnl_type in df['type'].sort_values().unique().tolist():
        df_plot = df[df['type'] == trmnl_type]
        fig.add_trace(go.Scattergeo(
            name=trmnl_type,
            lon=df_plot['longitude'],
            lat=df_plot['latitude'],
            text=df_plot['description'],
            marker=dict(
                # scale the bubbles according to their annual capacity
                size=df_plot['annual capacity'] / (4*(10**7)), #df_plot['annual capacity'].max() * 250,
                color=type_colour_dict[trmnl_type] if trmnl_type in type_colour_dict.keys() else 'red',
                opacity=0.6,
                line_color='black',
                line_width=0.6,
                sizemode='area'
            )
        ))

    fig.update_layout(
        height=800,
    )

    return fig


def stats_n_plots(df, year_filter, country_filter, type_filter):
    df = df[(df['start up date'] <= year_filter)]
    show_europe = True

    if type_filter:
        df = df[df.type.isin(type_filter)]

    ann_cap_eu = df['annual capacity'].sum()

    if country_filter:
        df = df[df.country.isin(country_filter)]
        show_europe = 'Europe' in country_filter

    # an_cap = df[df.country in country_filter]['annual capacity'].sum()

    fig = go.Figure()

    for trmnl_type in df['type'].sort_values().unique().tolist():
        df_bar = df[df['type'] == trmnl_type]
        type_countries = ['Europe'] + df_bar['country'].tolist() if show_europe else df_bar['country'].tolist()
        cap_country_type = [df_bar[df_bar.country == country]['annual capacity'].sum() for country in
                            df_bar.country.dropna().unique()]
        cap_plot = [ann_cap_eu] + cap_country_type if show_europe else cap_country_type
        fig.add_trace(go.Bar(
            x=type_countries,
            y=cap_plot,
            marker_color=type_colour_dict[trmnl_type],
            name=trmnl_type
        ))

    fig.update_layout(barmode='stack')

    fig.update_yaxes(title='Annual Capacity [m<sup>3</sup>]')

    fig.layout.showlegend = True

    return fig


df_map = read_terminals_db()
