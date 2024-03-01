import streamlit as st
import os
import json
import re
import requests
from random import randint
from time import sleep
from datetime import datetime, timedelta


@st.cache_data(ttl=60*60)
def get_NOAA(lat, lon):
    resp = requests.get(f"https://api.weather.gov/points/{lat},{lon}")
    first_page = resp.json()
    first_link = first_page.get("properties").get("forecastHourly")
    sleep(randint(1, 5))
    resp2 = requests.get(first_link)
    second_page = resp2.json()
    NOAA_hourly = second_page.get("properties").get("periods")
    start_time = NOAA_hourly[0]["startTime"]
    clean_str = start_time.replace('T', ' ')
    NOAA_time = re.sub(r"-[0-9][0-9]:00", '', clean_str)
    return NOAA_hourly, NOAA_time


@st.cache_data(ttl=60*60)
def get_merry_sky(lat, lon):
    m_weather = requests.get(f"https://api.merrysky.net/weather?q={lat},{lon}&source=pirateweather")
    m_json = m_weather.json()
    merry_sky_hourly = m_json.get("hourly").get("data")
    return merry_sky_hourly


def get_info(lat, lon):
    get_hourly, clean_time = get_NOAA(lat, lon)
    date_start = datetime.strptime(clean_time, '%Y-%m-%d %H:%M:%S')
    now = datetime.now()
    rounded_value = now.replace(second=0, microsecond=0, minute=0,
                                hour=now.hour)
    # now = now.strftime('%H:%M:%S')
    if rounded_value == date_start:
        i = 0
    else:
        i = 1

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
Wind: {wind_speed}, {wind_dir}   \nChance of Precip: {precip}%
Dewpoint: {dewpoint_F:.1f}F ({dewpoint_C:.1f}C)  \nRel Humidity: {rel_hum}%'''

    m_hourly = get_merry_sky(lat, lon)
    adj_now = rounded_value.timestamp()
    time2 = datetime.fromtimestamp(adj_now).strftime('%Y-%m-%d %H:%M:%S')
    for i in m_hourly:
        if i["time"] == adj_now:
            temp_C2 = i["temperature"]
            temp_F2 = (temp_C2 * 9/5) + 32
            feels_likeC = i["apparentTemperature"]
            feels_likeF = (feels_likeC * 9 / 5) + 32
            precip2 = i["precipProbability"] * 100
            dewpoint_C2 = i["dewPoint"]
            dewpoint_F2 = (dewpoint_C2 * 1.8) + 32
            rel_hum2 = i["humidity"] * 100
            wind_speed2 = i["windSpeed"] * 2.23694
            wind_gust2 = i["windGust"] * 2.23694
            windBearing2 = i["windBearing"]
            wind_dir2 = degToCompass(windBearing2)
            cloudiness2 = i["summary"]
            vis2 = i["visibility"] * 0.621371

    print_out2 = f'''
{cloudiness2}  \n{temp_F2:.01f}F ({temp_C2:.01f}C) 
Feels like: {feels_likeF:.01f}F ({feels_likeC:.01f}C)
Wind: {wind_dir2}, {wind_speed2:.01f} - {wind_gust2:.01f} mph  \nChance of Precip: {precip2}%
Dewpoint: {dewpoint_F2:.1f}F ({dewpoint_C2:.1f}C)  \nRel Humidity: {rel_hum2}%  \nVisibility: {vis2:.01f} mi'''

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"NOAA  \n{rounded_value} - 5hrs")
        st.code(print_out, language='None')
    with col2:
        st.write(f"Merry Sky  \n{time2} - 5hrs")
        st.code(print_out2, language='None')


def degToCompass(num):
    val=int((num/22.5)+.5)
    arr=["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    return arr[(val % 16)]


@st.cache_data
def load_eBird_hotspots(state):
    with open(f'resources/{state}_hotspots.json', encoding="utf-8") as f:
        eBird_hotspots = json.load(f)
    return eBird_hotspots


def location_value(col, hotspots, x, y):
    col_value = [d.get(col) for d in hotspots if d.get(x) == y]
    return col_value[0]


def main():
    # st.title("Weather")
    st.subheader("Hamlin Beach SP--No. 4")
    state = "NY"
    hotspot_data = load_eBird_hotspots(state)

    site = "Hamlin Beach SP--Parking Lot No. 4 (Primary Lakewatch site)"
    lat_input = location_value('lat', hotspot_data, 'locName', site)
    lon_input = location_value('lng', hotspot_data, 'locName', site)
    # st.write(lat_input, lon_input)
    get_info(lat_input, lon_input)


# Run main
if __name__ == "__main__":
    st.set_page_config(page_icon='🐦', initial_sidebar_state='expanded')

    main()
