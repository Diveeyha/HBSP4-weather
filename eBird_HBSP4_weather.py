import streamlit as st
import os
import json
import re
import requests
import pandas as pd
from datetime import datetime, timedelta


def get_info(lat, lon):
    resp = requests.get(f"https://api.weather.gov/points/{lat},{lon}")
    first_page = resp.json()
    first_link = first_page.get("properties").get("forecastHourly")

    resp2 = requests.get(first_link)
    second_page = resp2.json()
    get_hourly = second_page.get("properties").get("periods")
    start_time = get_hourly[0]["startTime"]
    clean_str = start_time.replace('T', ' ')
    clean_time = re.sub(r"-[0-9][0-9]:00", '', clean_str)
    date_start = datetime.strptime(clean_time, '%Y-%m-%d %H:%M:%S')
    now = datetime.now()
    rounded_value = now.replace(second=0, microsecond=0, minute=0,
                                hour=date_start.hour) + timedelta(hours=now.minute//30)
    now = now.strftime('%H:%M:%S')
    if rounded_value == date_start:
        i = 0
    else:
        i = 1

    num = get_hourly[i]["number"]
    temp_F = get_hourly[i]["temperature"]
    temp_C = (temp_F - 32) * 5/9
    precip = get_hourly[i]["probabilityOfPrecipitation"]["value"]
    dewpoint_C = get_hourly[i]["dewpoint"]["value"]
    dewpoint_F = (dewpoint_C * 1.8) + 32
    rel_hum = get_hourly[i]["relativeHumidity"]["value"]
    wind_speed = get_hourly[i]["windSpeed"]
    wind_dir = get_hourly[i]["windDirection"]
    cloudiness = get_hourly[i]["shortForecast"]
    if cloudiness == "fog":
        vis = "< 3,300 ft (1 km)"
    elif cloudiness == "mist":
        vis = "0.62 - 1.2 mi (1 - 2 km)"
    elif cloudiness == "haze":
        vis = "1.2 - 3.1 mi (2 - 5 km)"
    else:
        vis = "10.0 mi"
    print_out = f'''
{cloudiness}  \n{temp_F:.01f}F ({temp_C:.01f}C)
Wind: {wind_speed}, {wind_dir}   \nChance of Rain: {precip}%
Dewpoint: {dewpoint_F:.1f}F ({dewpoint_C:.1f}C)  \nRel Humidity: {rel_hum}%  \nVisibility: {vis}'''
    st.code(print_out, language='None')


@st.cache_data
def load_eBird_hotspots(state):
    with open(f'resources/{state}_hotspots.json', encoding="utf-8") as f:
        eBird_hotspots = json.load(f)
    return eBird_hotspots


def eBird_location_value(col, hotspots, site):
    col_value = [d.get(col) for d in hotspots if d.get('locName') == site]
    return col_value[0]


def main():
    st.title("Hamlin Beach SP--No. 4 Weather")
    state = "NY"
    hotspot_data = load_eBird_hotspots(state)

    site = "Hamlin Beach SP--Parking Lot No. 4 (Primary Lakewatch site)"
    lat_input = eBird_location_value('lat', hotspot_data, site)
    lon_input = eBird_location_value('lng', hotspot_data, site)
    # st.write(lat_input, lon_input)
    get_info(lat_input, lon_input)


# Run main
if __name__ == "__main__":
    st.set_page_config(page_icon='🐦', initial_sidebar_state='expanded')

    main()
