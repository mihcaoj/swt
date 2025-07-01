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
selected_station_name = st.selectbox("Select a Weather station:", station_names)

# Let user select a start/end date
one_year_ago = datetime.today() - timedelta(days=365)
selected_start_date = st.date_input(label="Select a Start Date:", value=one_year_ago, max_value="today", format="DD/MM/YYYY")
selected_end_date = st.date_input(label="Select a End Date:", max_value="today", format="DD/MM/YYYY")

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

station_data = get_station_data(selected_station['latitude'], selected_station['longitude'], selected_start_date, selected_end_date)

# Check if data is available
if all(col in station_data.columns for col in ['tavg', 'tmin', 'tmax']):
    st.subheader(f"Temperature in {selected_station_name} ({selected_start_date.strftime('%d.%m.%Y')}-{selected_end_date.strftime('%d.%m.%Y')})")
    temp_data = station_data[['tavg', 'tmin', 'tmax']].rename(columns={
        'tavg': 'Average Temperature',
        'tmin': 'Minimum Temperature',
        'tmax': 'Maximum Temperature'
    })
    st.line_chart(temp_data, x_label='Time', y_label='Temperature (°C)')
if all(col in station_data.columns for col in ['prcp']):
    st.subheader(f"Precipitation in {selected_station_name} ({selected_start_date.strftime('%d.%m.%Y')}-{selected_end_date.strftime('%d.%m.%Y')})")
    precipitation_data = station_data[['prcp']]
    st.bar_chart(precipitation_data, x_label='Time', y_label='Precipitation (mm)')
if all(col in station_data.columns for col in ['snow']):
    st.subheader(f"Snow in {selected_station_name} ({selected_start_date.strftime('%d.%m.%Y')}-{selected_end_date.strftime('%d.%m.%Y')})")
    snow_data = station_data[['snow']]
    st.bar_chart(snow_data, x_label='Time', y_label='Depth (mm)')
if all(col in station_data.columns for col in ['wspd', 'wpgt']):
    st.subheader(f"Wind in {selected_station_name} ({selected_start_date.strftime('%d.%m.%Y')}-{selected_end_date.strftime('%d.%m.%Y')})")
    wind_data = station_data[['wspd', 'wpgt']].rename(columns= {
        'wspd': 'Wind Speed',
        'wpgt': 'Wind Gusts'
    })
    st.area_chart(wind_data, x_label='Time', y_label='Kilometers per hour (km/h)')
if all(col in station_data.columns for col in ['pres']):
    st.subheader(f"Sea-level Air Pressure in {selected_station_name} ({selected_start_date.strftime('%d.%m.%Y')}-{selected_end_date.strftime('%d.%m.%Y')})")
    pres_data = station_data[['pres']]
    st.line_chart(pres_data, x_label='Time', y_label='Sea-level air pressure (hPa)')
if all(col in station_data.columns for col in ['tsun']):
    st.subheader(f"Sunshine in {selected_station_name} ({selected_start_date.strftime('%d.%m.%Y')}-{selected_end_date.strftime('%d.%m.%Y')})")
    sun_data = station_data[['tsun']]
    st.line_chart(sun_data, x_label='Time', y_label='Total sunshine (minutes)')
if station_data.empty:
    st.warning(f"No weather data available for {selected_station_name}")
