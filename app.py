import streamlit as st 
from datetime import datetime
from meteostat import Point, Daily, Stations, Hourly

st.header("Weather Data in Switzerland", divider="gray")

# Fetch Swiss stations
stations = Stations()
stations = stations.region('CH')
swiss_stations = stations.fetch()
swiss_stations = swiss_stations.dropna(subset=['name'])

# Start/End dates
start = datetime(2024, 1, 1)
end = datetime(2025, 1, 1)

# Let user select a station
station_names = swiss_stations['name'].tolist()
selected_station_name = st.selectbox("Select a Swiss weather station", station_names)

# Get the selected station's metadata (first match)
selected_station = swiss_stations[swiss_stations['name'] == selected_station_name].iloc[0]

# Create a Point from the station's latitude/longitude
station_point = Point(selected_station['latitude'], selected_station['longitude'])

# Fetch data for this station
station_data = Daily(station_point, start=start, end=end).fetch()

# Check if data is available
if 'tavg' and 'tmin' and 'tmax' in station_data.columns:
    st.subheader(f"Temperature in {selected_station_name} from {start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}")
    temp_data = station_data[['tavg', 'tmin', 'tmax']].rename(columns={
        'tavg': 'Average Temperature',
        'tmin': 'Minimum Temperature',
        'tmax': 'Maximum Temperature'
    })
    st.line_chart(temp_data, x_label='Time', y_label='Temperature (°C)')
if 'prcp' in station_data.columns:
    st.subheader(f"Precipitation in {selected_station_name} from {start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}")
    precipitation_data = station_data[['prcp']]
    st.bar_chart(precipitation_data, x_label='Time', y_label='Precipitation (mm)')
if 'wspd' and 'wpgt' in station_data.columns:
    st.subheader(f"Wind in {selected_station_name} from {start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}")
    wind_data = station_data[['wspd', 'wpgt']].rename(columns= {
        'wspd': 'Wind Speed',
        'wpgt': 'Wind Gusts'
    })
    st.area_chart(wind_data, x_label='Time', y_label='Kilometers per hour (km/h)')
else:
    st.warning(f"No weather data available for {selected_station_name}")
