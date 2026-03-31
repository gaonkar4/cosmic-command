import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Deep Space Command", layout="wide", page_icon="🔭")

# --- CONFIG ---
MY_KEY = "b0ee7c0ae9b84f1e8ff154503263003"

def get_moon_emoji(phase):
    phases = {
        "New Moon": "🌑", "Waxing Crescent": "🌒", "First Quarter": "🌓",
        "Waxing Gibbous": "🌔", "Full Moon": "🌕", "Waning Gibbous": "🌖",
        "Last Quarter": "🌗", "Waning Crescent": "🌘"
    }
    return phases.get(phase, "🌙")

def get_cosmic_data():
    try:
        # 1. AUTO-LOCATION (The Ground Station)
        geo = requests.get("http://ip-api.com/json/").json()
        lat, lon, city = geo['lat'], geo['lon'], geo['city']

        # 2. SKY & ATMOSPHERE DATA (WeatherAPI)
        # We use 'forecast' instead of 'astronomy' to get Cloud Cover
        w_url = f"http://api.weatherapi.com/v1/forecast.json?key={MY_KEY}&q={lat},{lon}&days=1&aqi=no"
        w_data = requests.get(w_url).json()
        
        astro = w_data['forecast']['forecastday'][0]['astro']
        current = w_data['current']
        clouds = current['cloud'] # Cloud cover %

        # 3. LIVE ISS TRACKER (International Space Station)
        iss = requests.get("http://api.open-notify.org/iss-now.json").json()
        iss_lat = float(iss['iss_position']['latitude'])
        iss_lon = float(iss['iss_position']['longitude'])

        # 4. NASA PHOTO OF THE DAY
        nasa = requests.get("https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY").json()

        # --- UI DESIGN ---
        st.title("🛰️ Deep Space Command Center")
        st.caption(f"Ground Station: {city} | Connection: STABLE")

        # NASA IMAGE HEADER
        with st.expander("📡 LATEST NASA DEEP SPACE INTELLIGENCE", expanded=True):
            st.image(nasa.get('url'), use_container_width=True)
            st.info(f"**Object:** {nasa.get('title')}")

        # ROW 1: MISSION METRICS
        st.divider()
        m1, m2, m3, m4 = st.columns(4)
        
        m1.metric("Moon Phase", f"{get_moon_emoji(astro['moon_phase'])} {astro['moon_phase']}")
        m2.metric("Illumination", f"{astro['moon_illumination']}%")
        m3.metric("Cloud Cover", f"{clouds}%")
        
        # Visibility Logic
        if clouds < 20 and int(astro['moon_illumination']) < 30:
            status = "💎 PERFECT VIEWING"
        elif clouds > 70:
            status = "☁️ SKY BLOCKED"
        else:
            status = "✨ FAIR CONDITIONS"
        m4.metric("Stargazing Score", status)

        # ROW 2: LIVE RADAR (YOU VS. THE ISS)
        st.subheader("🌍 Real-Time Satellite Tracking")
        # Creating a dataframe for the map with two points
        map_df = pd.DataFrame({
            'lat': [lat, iss_lat],
            'lon': [lon, iss_lon],
            'color': ['#0000FF', '#FF0000'] # Blue for you, Red for ISS
        })
        st.map(map_df)
        st.write(f"The **ISS** is currently orbiting at 17,500 mph over `{iss_lat}, {iss_lon}`")

        # ROW 3: ENVIRONMENTAL INTEL
        st.divider()
        left, right = st.columns(2)
        
        with left:
            st.subheader("☀️ Solar Intel")
            st.write(f"🌅 **Sunrise:** `{astro['sunrise']}`")
            st.write(f"🌇 **Sunset:** `{astro['sunset']}`")
            st.write(f"🔥 **UV Index:** `{current['uv']}`")

        with right:
            st.subheader("🌙 Lunar Intel")
            st.write(f"⬆️ **Moonrise:** `{astro['moonrise']}`")
            st.write(f"⬇️ **Moonset:** `{astro['moonset']}`")
            st.write(f"🌊 **Local Temp:** `{current['temp_c']}°C`")

    except Exception as e:
        st.error(f"Uplink Error: {e}")

get_cosmic_data()
