import streamlit as st 
from datetime import datetime, timedelta
from meteostat import Point, Daily, Stations

st.set_page_config(
    page_title="SwissWeatherTracker",
    page_icon="static/favicon.ico"
)
st.logo('static/swt-logo-transparent.png', size="large")
st.header("Swiss Weather Data Visualizer", divider="gray")

# Fetch Swiss stations
stations = Stations()
stations = stations.region('CH')
swiss_stations = stations.fetch()
swiss_stations = swiss_stations.dropna(subset=['name'])

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

# Fetch data for this station
station_data = Daily(station_point, start=selected_start_date, end=selected_end_date).fetch()

# Check if data is available
if 'tavg' and 'tmin' and 'tmax' in station_data.columns:
    st.subheader(f"Temperature in {selected_station_name} ({selected_start_date.strftime('%d.%m.%Y')}-{selected_end_date.strftime('%d.%m.%Y')})")
    temp_data = station_data[['tavg', 'tmin', 'tmax']].rename(columns={
        'tavg': 'Average Temperature',
        'tmin': 'Minimum Temperature',
        'tmax': 'Maximum Temperature'
    })
    st.line_chart(temp_data, x_label='Time', y_label='Temperature (°C)')
if 'prcp' in station_data.columns:
    st.subheader(f"Precipitation in {selected_station_name} ({selected_start_date.strftime('%d.%m.%Y')}-{selected_end_date.strftime('%d.%m.%Y')})")
    precipitation_data = station_data[['prcp']]
    st.bar_chart(precipitation_data, x_label='Time', y_label='Precipitation (mm)')
if 'snow' in station_data.columns:
    st.subheader(f"Snow in {selected_station_name} ({selected_start_date.strftime('%d.%m.%Y')}-{selected_end_date.strftime('%d.%m.%Y')})")
    snow_data = station_data[['snow']]
    st.bar_chart(snow_data, x_label='Time', y_label='Depth (mm)')
if 'wspd' and 'wpgt' in station_data.columns:
    st.subheader(f"Wind in {selected_station_name} ({selected_start_date.strftime('%d.%m.%Y')}-{selected_end_date.strftime('%d.%m.%Y')})")
    wind_data = station_data[['wspd', 'wpgt']].rename(columns= {
        'wspd': 'Wind Speed',
        'wpgt': 'Wind Gusts'
    })
    st.area_chart(wind_data, x_label='Time', y_label='Kilometers per hour (km/h)')
if 'pres' in station_data.columns:
    st.subheader(f"Sea-level Air Pressure in {selected_station_name} ({selected_start_date.strftime('%d.%m.%Y')}-{selected_end_date.strftime('%d.%m.%Y')})")
    pres_data = station_data[['pres']]
    st.line_chart(pres_data, x_label='Time', y_label='Sea-level air pressure (hPa)')
if 'tsun' in station_data.columns:
    st.subheader(f"Sunshine in {selected_station_name} ({selected_start_date.strftime('%d.%m.%Y')}-{selected_end_date.strftime('%d.%m.%Y')})")
    sun_data = station_data[['tsun']]
    st.line_chart(sun_data, x_label='Time', y_label='Total sunshine (minutes)')
else:
    st.warning(f"No weather data available for {selected_station_name}")
