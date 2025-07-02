import streamlit as st
from datetime import datetime, timedelta
from meteostat import Point, Daily, Stations

st.set_page_config(
    page_title="SwissWeatherTracker",
    page_icon="static/favicon.ico",
    # initial_sidebar_state="collapsed"
)
st.logo('static/swt-logo-transparent.png', size="large")
st.header("Swiss Weather Data Visualizer", divider="gray")

# Fetch Swiss stations - time-to-live is 24h (86400 seconds)
@st.cache_data(ttl=86400)
def get_swiss_stations():
    swiss_stations = Stations().region('CH').fetch()
    return swiss_stations.dropna(subset=['name'])

swiss_stations = get_swiss_stations()

# Let user select a station
station_names = swiss_stations['name'].tolist()
selected_station_name = st.selectbox("Select Weather station:", station_names)

# Let user select a start/end date
one_year_ago = datetime.today() - timedelta(days=365)
selected_start_date = st.date_input(label="Select Start Date:", value=one_year_ago, max_value="today", format="DD/MM/YYYY")
selected_end_date = st.date_input(label="Select End Date:", max_value="today", format="DD/MM/YYYY")

# Convert date to datetime
selected_start_date = datetime.combine(selected_start_date, datetime.min.time())
selected_end_date = datetime.combine(selected_end_date, datetime.min.time())

# Get the selected station's metadata (first match)
selected_station = swiss_stations[swiss_stations['name'] == selected_station_name].iloc[0]

# Create a Point from the station's latitude/longitude
station_point = Point(selected_station['latitude'], selected_station['longitude'])

# Fetch data for this station - time-to-live is 24h (86400 seconds)
@st.cache_data(ttl=86400)
def get_station_data(lat, lon, start_date, end_date):
    point = Point(lat, lon)
    return Daily(point, start=start_date, end=end_date).fetch()

options = ["All", "Temperature", "Precipitation", "Snow", "Wind", "Pressure", "Sunshine"]
selection = st.pills("Filter:", options, selection_mode="multi", default=["All"])

station_data = get_station_data(selected_station['latitude'], selected_station['longitude'], selected_start_date, selected_end_date)

if station_data.empty:
    st.warning(f"No weather data available for {selected_station_name}")

def highlight_text(content):
    '''Return content wrapped in a subtle span to highlight it'''
    return (
        f"<span style='border: 1.5px solid rgba(200, 200, 200, 0.4);"
        "padding: 3px 7px; border-radius: 5px;"
        "background-color: rgba(220, 220, 220, 0.07);"
        "color: inherit;'>"
        f"{content}"
        "</span>"
    )

def render_temperature(data, station_name, start_date, end_date):
    if all(col in data.columns for col in ['tavg', 'tmin', 'tmax']):
        highlighted_text = highlight_text(f"{station_name} ({start_date.strftime('%d.%m.%Y')}-{end_date.strftime('%d.%m.%Y')})")
        st.markdown(f"<h3>Temperature in {highlighted_text}</h3>", unsafe_allow_html=True)
        temp_data = data[['tavg', 'tmin', 'tmax']].rename(columns={
            'tavg': 'Average Temperature',
            'tmin': 'Minimum Temperature',
            'tmax': 'Maximum Temperature'
        })
        st.line_chart(temp_data, x_label='Time', y_label='Temperature (°C)', color=["#1d4ed8", "#e63946", "#0ea5e9"], height=500)

def render_precipitation(data, station_name, start_date, end_date):
    if all(col in data.columns for col in ['prcp']):
        highlighted_text = highlight_text(f"{station_name} ({start_date.strftime('%d.%m.%Y')}-{end_date.strftime('%d.%m.%Y')})")
        st.markdown(f"<h3>Precipitation in {highlighted_text}</h3>", unsafe_allow_html=True)
        precipitation_data = data[['prcp']]
        st.bar_chart(precipitation_data, x_label='Time', y_label='Precipitation (mm)', height=500)

def render_snow(data, station_name, start_date, end_date):
    if all(col in data.columns for col in ['snow']):
        highlighted_text = highlight_text(f"{station_name} ({start_date.strftime('%d.%m.%Y')}-{end_date.strftime('%d.%m.%Y')})")
        st.markdown(f"<h3>Snow in {highlighted_text}</h3>", unsafe_allow_html=True)
        snow_data = data[['snow']]
        st.bar_chart(snow_data, x_label='Time', y_label='Depth (mm)', height=500)

def render_wind(data, station_name, start_date, end_date):
    if all(col in data.columns for col in ['wspd', 'wpgt']):
        highlighted_text = highlight_text(f"{station_name} ({start_date.strftime('%d.%m.%Y')}-{end_date.strftime('%d.%m.%Y')})")
        st.markdown(f"<h3>Wind in {highlighted_text}</h3>", unsafe_allow_html=True)
        wind_data = data[['wspd', 'wpgt']].rename(columns= {
            'wspd': 'Wind Speed',
            'wpgt': 'Wind Gusts'
        })
        st.area_chart(wind_data, x_label='Time', y_label='Kilometers per hour (km/h)', height=500)

def render_pressure(data, station_name, start_date, end_date):
    if all(col in data.columns for col in ['pres']):
        highlighted_text = highlight_text(f"{station_name} ({start_date.strftime('%d.%m.%Y')}-{end_date.strftime('%d.%m.%Y')})")
        st.markdown(f"<h3>Pressure in {highlighted_text}</h3>", unsafe_allow_html=True)
        pres_data = data[['pres']]
        st.line_chart(pres_data, x_label='Time', y_label='Sea-level air pressure (hPa)', height=500)

def render_sunshine(data, station_name, start_date, end_date):
    if all(col in data.columns for col in ['tsun']):
        highlighted_text = highlight_text(f"{station_name} ({start_date.strftime('%d.%m.%Y')}-{end_date.strftime('%d.%m.%Y')})")
        st.markdown(f"<h3>Sunshine in {highlighted_text}</h3>", unsafe_allow_html=True)
        sun_data = data[['tsun']]
        st.line_chart(sun_data, x_label='Time', y_label='Total sunshine (minutes)', height=500)

renderers = {
    "Temperature": render_temperature,
    "Precipitation": render_precipitation,
    "Snow": render_snow,
    "Wind": render_wind,
    "Pressure": render_pressure,
    "Sunshine": render_sunshine,
}

if not station_data.empty:
    if "All" in selection:
        for func in renderers.values():
            func(station_data, selected_station_name, selected_start_date, selected_end_date)
    else:
        for option in selection:
            if option in renderers:
                renderers[option](station_data, selected_station_name, selected_start_date, selected_end_date)
