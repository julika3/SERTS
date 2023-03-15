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

    # m^3 to kWh via the calorific value (SERTS Wrap Up p. 201)
    # natural gas (L): 8,4 - 10,2 kWh/m^3
    cal_val_l_min = 8.4
    df_db['min capacity [kWh]'] = df_db['annual capacity'] * cal_val_l_min
    # natural gas (H): 11,1 - 13,1 kWh/m^3
    cal_val_h_max = 13.1
    df_db['max capacity [kWh]'] = df_db['annual capacity'] * cal_val_h_max

    # assign an out-of-scope start up date to terminals with unknown start up years to make them visible in map
    df_db['start up date'] = df_db['start up date'].map(lambda x: 2031 if x == '?' else x)

    return df_db


def create_map(df, year):
    lonaxis_range = [df['longitude'].min() - 10, df['longitude'].max() + 10]
    lataxis_range = [df['latitude'].min() - 0.5, df['latitude'].max() + 2]

    # filter dataframe for terminals build before or in selected year
    df = df[df['start up date'] <= year]

    # aggregate facilities and their expansions
    df_map = df.groupby(['latitude', 'longitude', 'type']).first()
    df_map['annual capacity'] = df.groupby(['latitude', 'longitude', 'type'])['annual capacity'].sum()
    df_map['min capacity [kWh]'] = df.groupby(['latitude', 'longitude', 'type'])['min capacity [kWh]'].sum()
    df_map['max capacity [kWh]'] = df.groupby(['latitude', 'longitude', 'type'])['max capacity [kWh]'].sum()
    df_map['latitude'], df_map['longitude'], df_map['type'] = zip(*df_map.index)
    df_map.reset_index(drop=True, inplace=True)

    # description to be displayed in as hover text (html formatting)
    df_map['description'] = 'Location: ' + df_map['location'] \
                            + '<br>Type: ' + df_map['type'] \
                            + '<br>Start up Date: ' + df_map['start up date'].astype(str) \
                            + '<br>Annual Capacity [billion m<sup>3</sup>]: ' \
                            + df_map['annual capacity'].map(lambda x: x / 10 ** 9).astype(str) \
                            + '<br>Annual Capacity [TWh]: ' + df_map['min capacity [kWh]'].map(lambda x: x / 10 ** 9).astype(str) \
                            + ' - ' + df_map['max capacity [kWh]'].map(lambda x: x / 10 ** 9).astype(str)

    fig = go.Figure()

    fig.update_layout(
        title='LNG Terminals in Europe',
        title_x=0.43,
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
            lonaxis_range=lonaxis_range,
            lataxis_range=lataxis_range,
        ),
    )

    # add the terminals to the map via their latitude and longitude coordinates
    for trmnl_type in df_map['type'].sort_values().unique().tolist():
        df_plot = df_map[df_map['type'] == trmnl_type]
        fig.add_trace(go.Scattergeo(
            name=trmnl_type,
            lon=df_plot['longitude'],
            lat=df_plot['latitude'],
            text=df_plot['description'],
            marker=dict(
                # scale the bubbles according to their annual capacity
                # except if capacity is zero, then give it a default value to make it visible
                size=(df_plot['annual capacity'] / (4*(10**7))).map(lambda x: 5 if x == 0 else x),
                color=type_colour_dict[trmnl_type] if trmnl_type in type_colour_dict.keys() else 'red',
                opacity=0.6,
                line_color='black',
                line_width=0.6,
                sizemode='area'
            )
        ))

    fig.update_layout(
        height=700,
    )

    return fig


def stats_n_plots(df, year_filter, country_filter, type_filter):
    df = df[(df['start up date'] <= year_filter)]
    show_europe = False

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
        country_type = df_bar.country.dropna().sort_values().unique().tolist()
        countries_plot = ['Europe'] + country_type if show_europe else country_type
        cap_country_type = [df_bar[df_bar.country == country]['annual capacity'].sum() for country in countries_plot]
        cap_plot = [ann_cap_eu] + cap_country_type if show_europe else cap_country_type

        fig.add_trace(go.Bar(
            x=countries_plot,
            y=cap_plot,
            marker_color=type_colour_dict[trmnl_type],
            name=trmnl_type
        ))

    fig.update_layout(barmode='stack')

    fig.update_yaxes(title='Annual Capacity [m<sup>3</sup>]')

    fig.layout.showlegend = True

    return fig


def plot_demand(df_lng, df_demand, country_filter, year):

    if not country_filter:
        country_filter = df_demand['country'].sort_values().unique().tolist()

    df_lng = df_lng[df_lng['start up date'] <= year]

    fig = go.Figure()

    fig.update_layout(title=f'Demand and LNG Capacities in in {year}')

    for country in country_filter:
        df_lng_temp = df_lng[df_lng.country == country].sum() if country != 'Europe' else df_lng.sum()
        lng_cap_l = df_lng_temp['min capacity [kWh]']
        lng_cap_h = df_lng_temp['max capacity [kWh]']

        df_demand_temp = df_demand[df_demand.country == country].sum() if country != 'Europe' \
                                                                            else df_demand.sum()
        demand = df_demand_temp['Total 2021']

        fig.add_trace(
            go.Bar(
                x=['Demand (2021)', 'LNG Supply (L Gas)', 'LNG Supply (H Gas)'],
                y=[x / 10**9 for x in (demand, lng_cap_l, lng_cap_h)],
                name=country
            )
        )

    fig.update_layout(barmode='stack')

    fig.layout.showlegend = True

    fig.update_yaxes(title='Annual LNG Capacities / Gas Demand [TWh]')

    return fig


df_map = read_terminals_db()
df_demand = pd.read_excel('Production&Demand.xlsx', sheet_name='demand_storage_kWh')
european_demand = df_demand['Total 2021'].sum()
