import plotly.graph_objects as go
from plotly.express import colors
import pandas as pd

## constants for the filnames. for files in different directories the path may also be added to the filename
## additionally constants for variable names taken from database table headers
# LNG Terminals
LNG_DB_FILENAME = 'database.xlsx'

# column names
CAPACITY = 'annual capacity'
COUNTRY = 'country'
LOCATION = 'location'
LATITUDE = 'latitude'
LONGITUDE = 'longitude'
START_UP_DATE = 'start up date'
TYPE = 'type'

# m^3 to kWh via the calorific value (DVGW G 260)
# natural gas (L): 8,4 - 10,2 kWh/m^3
# natural gas (H): 11,1 - 13,1 kWh/m^3
CAL_VAL_MAX = 13.1
CAL_VAL_MIN = 8.4

# Demand
DEMAND_DB_FILENAME = 'Production&Demand.xlsx'
DEMAND_DB_SHEET = 'demand_storage_kWh'

# column name
DEMAND_2021 = 'Total 2021'
PERCENTAGE_RG = 'Percentage Russian Gas'
# COUNTRY = lng_terminals COUNTRY


# set colours for the different terminal types to use for both the map and stats
# within the functions red is declared as a fallback color if the name isn't one of these
type_colour_dict = {'FRU + direct link to UGS': 'darkblue',
                    'FSRU': 'cornflowerblue',
                    'FSU and onshore Regasification': 'seagreen',
                    'offshore GBS': 'slateblue',
                    'onshore facility': 'olive'
                    }

# a list of plotly colour codes
# after importing the database colours a unique colour is assigned to each country
color_variety = colors.qualitative.Alphabet + colors.qualitative.Set3 + colors.qualitative.Antique


def read_databases():
    # prepare the dataframe vor visualisation
    df_capacity = pd.read_excel(LNG_DB_FILENAME, skiprows=0)
    # some terminals which are still being built haven't published a final capacity yet
    # these unknown capacities aren't estimated in this model and instead appear as zero
    df_capacity[CAPACITY] = df_capacity[CAPACITY].map(lambda x: 0 if x == '?' else float(x))
    df_capacity[LATITUDE] = df_capacity[LATITUDE].map(lambda x: float(x))
    df_capacity[LONGITUDE] = df_capacity[LONGITUDE].map(lambda x: float(x))

    # converting the volumetric capacities to energetic values
    df_capacity['min capacity [kWh]'] = df_capacity[CAPACITY] * CAL_VAL_MIN
    df_capacity['max capacity [kWh]'] = df_capacity[CAPACITY] * CAL_VAL_MAX

    # assign an out-of-scope start up date to terminals with unknown start up years to make them visible in map
    # these start up dates are unknown bc the completion date isn't final yet
    df_capacity[START_UP_DATE] = df_capacity[START_UP_DATE].map(lambda x: 2031 if x == '?' else x)

    df_demand = pd.read_excel(DEMAND_DB_FILENAME, sheet_name=DEMAND_DB_SHEET)
    df_demand['russian gas'] = df_demand[DEMAND_2021] * df_demand[PERCENTAGE_RG]

    return df_capacity, df_demand


def create_map(df, year):
    # set range for map around the maximum coordinates in database
    lonaxis_range = [df[LONGITUDE].min() - 10, df[LONGITUDE].max() + 10]
    lataxis_range = [df[LATITUDE].min() - 0.5, df[LATITUDE].max() + 2]

    # filter dataframe for terminals build before or in selected year
    df = df[df[START_UP_DATE] <= year]

    # aggregate facilities and their expansions
    df_map = df.groupby([LATITUDE, LONGITUDE, TYPE]).first()
    df_map[CAPACITY] = df.groupby([LATITUDE, LONGITUDE, TYPE])[CAPACITY].sum()
    df_map['min capacity [kWh]'] = df.groupby([LATITUDE, LONGITUDE, TYPE])['min capacity [kWh]'].sum()
    df_map['max capacity [kWh]'] = df.groupby([LATITUDE, LONGITUDE, TYPE])['max capacity [kWh]'].sum()
    df_map[LATITUDE], df_map[LONGITUDE], df_map[TYPE] = zip(*df_map.index)
    df_map.reset_index(drop=True, inplace=True)

    # description to be displayed in as hover text (html formatting)
    df_map['description'] = 'Location: ' + df_map[LOCATION] + ' ' + df_map[COUNTRY]\
                            + '<br>Type: ' + df_map[TYPE] \
                            + '<br>Start up Date: ' + df_map[START_UP_DATE].astype(str) \
                            + '<br>Annual Capacity [billion m<sup>3</sup>]: ' \
                            + df_map[CAPACITY].map(lambda x: x / 10 ** 9).astype(str) \
                            + '<br>Annual Capacity [TWh]: ' + df_map['min capacity [kWh]'].map(lambda x: x / 10 ** 9).astype(str) \
                            + ' - ' + df_map['max capacity [kWh]'].map(lambda x: x / 10 ** 9).astype(str)

    fig = go.Figure()

    # create map
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
    for trmnl_type in df_map[TYPE].sort_values().unique().tolist():
        df_plot = df_map[df_map[TYPE] == trmnl_type]
        fig.add_trace(go.Scattergeo(
            name=trmnl_type,
            lon=df_plot[LONGITUDE],
            lat=df_plot[LATITUDE],
            text=df_plot['description'],
            marker=dict(
                # scale the bubbles according to their annual capacity
                # except if capacity is zero, then give it a default value to make it visible
                size=(df_plot[CAPACITY] / (4 * (10 ** 7))).map(lambda x: 5 if x == 0 else x),
                color=type_colour_dict[trmnl_type] if trmnl_type in type_colour_dict.keys() else 'red',
                opacity=0.6,
                line_color='black',
                line_width=0.6,
                sizemode='area'
            )
        ))

    fig.update_layout(height=700)

    return fig


def plot_terminal_capacities(df_lng, year_filter, country_filter=None, type_filter=None):
    df_lng = df_lng[(df_lng[START_UP_DATE] <= year_filter)]

    if type_filter is not None:
        df_lng = df_lng[df_lng[TYPE].isin(type_filter)]
    else:
        # if no type filter is set show all types
        type_filter = df_lng[TYPE].sort_values().unique().tolist()

    if country_filter is not None:
        show_europe = 'Europe' in country_filter
    else:
        # if no filter is set show all individual countries
        country_filter = df_lng[COUNTRY].sort_values().unique().tolist()
        show_europe = False

    fig = go.Figure()

    # individual traces are added per terminal type
    for trmnl_type in type_filter:
        df_bar = df_lng[df_lng[TYPE] == trmnl_type]

        # get all countries which have terminals of the current iteration type and are part of the selected filter
        # add europe if the filter was selected
        country_type = [cntry for cntry in df_bar[COUNTRY].sort_values().unique().tolist() if cntry in country_filter]
        countries_plot = ['Europe'] + country_type if show_europe else country_type
        # sum up capacities for each country with the terminal type thats in the selected filter, convert to billion m^3
        # add an unfiltered sum for europe if selected
        cap_country_type = [df_bar[df_bar[COUNTRY] == country][CAPACITY].sum() / 10**9 for country in country_type]
        cap_plot = [df_bar[CAPACITY].sum() / 10**9] + cap_country_type if show_europe else cap_country_type

        fig.add_trace(go.Bar(
            x=countries_plot,
            y=cap_plot,
            marker_color=type_colour_dict[trmnl_type],
            name=trmnl_type
        ))

    fig.update_yaxes(title='Annual Capacity [billion m<sup>3</sup>]')
    fig.update_layout(title=f'Annual LNG Capacities in {year_filter}')
    fig.update_layout(barmode='stack', showlegend=True, legend={'traceorder': 'normal'})

    return fig


def plot_demand(df_lng, df_demand, year, country_filter=None):
    # if no filter for the countries is selected visualise all countries in database
    if country_filter is None:
        country_filter = df_demand[COUNTRY].sort_values().unique().tolist()
    # if europe is part of the selection it's nonsensical to add other countries too as they're already incorporated
    elif 'Europe' in country_filter:
        country_filter = ['Europe']

    # set selected year filter
    df_lng = df_lng[df_lng[START_UP_DATE] <= year]

    fig = go.Figure()

    # individual traces are added for each country
    for country in country_filter:
        # filter for the current country except if the selection is europe in that case sum everything up
        # summing up also needed for the country filtered dataframe because of multiple terminals/extensions
        df_lng_temp = df_lng[df_lng[COUNTRY] == country].sum(numeric_only=True) if country != 'Europe' \
                                                                                else df_lng.sum(numeric_only=True)
        df_demand_temp = df_demand[df_demand[COUNTRY] == country].sum() if country != 'Europe' \
                                                                            else df_demand.sum()

        # get the desired values from the aggregated dataframes
        lng_cap_l = df_lng_temp['min capacity [kWh]']
        lng_cap_h = df_lng_temp['max capacity [kWh]']
        demand = df_demand_temp[DEMAND_2021]
        demand_rg = df_demand_temp['russian gas']

        # create trace in bar chart format, convert from kWh to TWh
        fig.add_trace(
            go.Bar(
                x=['Total Demand (2021)', 'Demand for Russian Gas (2021)', 'LNG Supply (L Gas)', 'LNG Supply (H Gas)'],
                y=[x / 10**9 for x in (demand, demand_rg, lng_cap_l, lng_cap_h)],
                name=country,
                marker_color=country_colour_dict[country] if country in country_colour_dict.keys() else 'red'
            )
        )

    fig.update_yaxes(title='Annual LNG Capacities / Gas Demand [TWh]')
    fig.update_layout(title=f'Demand and LNG Capacities in {year}')
    fig.update_layout(barmode='stack', showlegend=True, legend={'traceorder': 'normal'})

    return fig


# Databases dataframes
df_lng_terminals, df_demand_2021 = read_databases()

# assign a unique colour to be used in the plots for each country and one for 'Europe'
country_colour_dict = dict((country, color_variety[n]) for n, country in
                           enumerate(df_demand_2021[COUNTRY].dropna().sort_values().unique().tolist() + ['Europe']))
