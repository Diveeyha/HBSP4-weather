import streamlit as st
import json
import requests
from datetime import datetime
from dateutil import tz


@st.cache_data(ttl=60*60)
def get_merry_sky(lat, lon):
    m_weather = requests.get(f"https://api.merrysky.net/weather?q={lat},{lon}&source=pirateweather")
    m_json = m_weather.json()
    merry_sky_hourly = m_json.get("hourly").get("data")
    return merry_sky_hourly


def get_info(lat, lon):
    now = datetime.now()
    rounded_value = now.replace(second=0, microsecond=0, minute=0, hour=now.hour)
    m_hourly = get_merry_sky(lat, lon)
    adj_now = rounded_value.timestamp()
    time = datetime.fromtimestamp(adj_now)
    for i in m_hourly:
        if i["time"] == adj_now:
            temp_C = i["temperature"]
            temp_F = (temp_C * 9/5) + 32
            feels_likeC = i["apparentTemperature"]
            feels_likeF = (feels_likeC * 9 / 5) + 32
            precip = i["precipProbability"] * 100
            dewpoint_C = i["dewPoint"]
            dewpoint_F = (dewpoint_C * 1.8) + 32
            rel_hum = i["humidity"] * 100
            wind_speed = i["windSpeed"] * 2.23694
            wind_gust = i["windGust"] * 2.23694
            windBearing = i["windBearing"]
            wind_dir = degToCompass(windBearing)
            cloudiness = i["summary"]
            cloud_cover = i["cloudCover"] * 100
            vis = i["visibility"] * 0.621371
            precip_amount = round(i["precipAccumulation"]/25.4, 1)
            precip_type = i["precipType"]

    print_out2 = f'''
{cloudiness}, {temp_F:.1f}F/{temp_C:.1f}C
Feel: {feels_likeF:.1f}F/{feels_likeC:.1f}C 
Wind: {wind_dir}, {wind_speed:.1f} - {wind_gust:.1f}mph
Clouds: {cloud_cover}%
Precip: {precip:.1f}%{'' if precip_amount < 0.1 else f", {precip_amount}in of {precip_type}"}
Rel Humidity: {rel_hum:.1f}%
Dewpoint: {dewpoint_F:.1f}F ({dewpoint_C:.1f}C)
Visibility: {vis:.01f}mi
Last update: {time.astimezone(tz.gettz('America/New_York')).strftime('%Y-%m-%d %H:%M:%S')}'''

    st.code(print_out2, language='None')


def degToCompass(num):
    val = int((num/22.5)+.5)
    arr = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
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
    st.subheader(f"WEATHER: [Hamlin Beach SP #4](https://ebird.org/hotspot/L139811)")
    state = "NY"
    hotspot_data = load_eBird_hotspots(state)

    site = "Hamlin Beach SP--Parking Lot No. 4 (Primary Lakewatch site)"
    lat_input = location_value('lat', hotspot_data, 'locName', site)
    lon_input = location_value('lng', hotspot_data, 'locName', site)
    get_info(lat_input, lon_input)


# Run main
if __name__ == "__main__":
    st.set_page_config(page_icon='💦', initial_sidebar_state='expanded')
    main()
