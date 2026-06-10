import streamlit as st
import pandas as pd
from weather import get_current_weather, get_forecast
from location import get_user_location
from datetime import datetime
import plotly.express as px
import requests
from streamlit_lottie import st_lottie
import json

def dynamic_sky(weather_main):
    weather_main = weather_main.lower()

    if "rain" in weather_main:
        bg = """
        <style>
        .stApp {
            background: linear-gradient(to bottom, #0f2027, #203a43, #2c5364);
            color: white;
        }
        </style>
        """

    elif "cloud" in weather_main:
        bg = """
        <style>
        .stApp {
            background: linear-gradient(to bottom, #bdc3c7, #2c3e50);
            color: black;
        }
        </style>
        """

    elif "clear" in weather_main:
        bg = """
        <style>
        .stApp {
            background: linear-gradient(to bottom, #56ccf2, #2f80ed);
            color: white;
        }
        </style>
        """

    else:
        bg = """
        <style>
        .stApp {
            background: linear-gradient(to bottom, #e0eafc, #cfdef3);
            color: black;
        }
        </style>
        """

    st.markdown(bg, unsafe_allow_html=True)

def load_local_lottie(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data
def load_lottie(url):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

def weather_card(title, value, emoji, color):
    st.markdown(f"""
    <div style="
        padding: 20px;
        border-radius: 15px;
        background: linear-gradient(135deg, {color});
        color: white;
        text-align: center;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.2);
        margin: 10px 0;
        transition: transform 0.3s ease;
    ">
        <div style="font-size: 30px;">{emoji}</div>
        <h3 style="margin: 5px 0;">{title}</h3>
        <h2 style="margin: 0;">{value}</h2>
    </div>
    """, unsafe_allow_html=True)


if "history" not in st.session_state:
    st.session_state.history = []

st.set_page_config(page_title = "Weather Forecast App", page_icon = "🌥️", layout = "wide")

st.markdown("""
<style>
h1, h2, h3, h4, h5, h6,
p, label, span, div,
[data-testid="stMetricValue"],
[data-testid="stMetricLabel"] {
    color: white !important;
}

section[data-testid="stSidebar"] * {
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.stApp {
    transition: background 1s ease-in-out;
}
</style>
""", unsafe_allow_html=True)

detected_city = get_user_location()

st.markdown("""#  Weather Forecast App""")
st.sidebar.markdown("### Search History")

for c in st.session_state.history[-5:]:
    st.sidebar.write("•", c)

st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if detected_city:
    st.info(f"Detected Location: {detected_city}")

use_location = st.button(" Use My Current Location")

refresh = st.button(" Refresh Data")

if use_location and detected_city:
    city = detected_city

else:
    city = st.text_input("Enter City Name", value=detected_city if detected_city else "")

if not city:
    st.stop()
    
get_weather = st.button("Get Weather")

if get_weather and city:
    with st.spinner("Fetching weather data..."):
        data = get_current_weather(city)

        if not data or "coord" not in data:
            st.error("⚠️ Unable to fetch weather data. Try another city.")
            st.stop()

        if city not in st.session_state.history:
            st.session_state.history.append(city)

        forecast_data = get_forecast(city)
        
        if not forecast_data or "list" not in forecast_data:
            st.error("⚠️ Forecast not available.")
            st.stop()

        temp = data.get("main", {}).get("temp", 0)
        weather_main = data.get("weather", [{}])[0].get("main", "").lower()
        dynamic_sky(weather_main)
        
        if temp >= 35:
            temp_state = "🔥 Hot"
        elif temp >= 25:
            temp_state = "🌤️ Warm"
        elif temp >= 15:
            temp_state = "🌥️ Cool"
        else:
            temp_state = "❄️ Cold"

        if "rain" in weather_main:
            condition = "🌧️ Rainy"
        elif "cloud" in weather_main:
            condition = "☁️ Cloudy"
        elif "clear" in weather_main:
            condition = "☀️ Clear"
        else:
            condition = "🌫️ Mixed"

        weather_animation = None

        if "rain" in weather_main:
            weather_animation = load_local_lottie("animations/rain.json")

        elif "cloud" in weather_main:
            weather_animation = load_local_lottie("animations/cloud.json")

        elif "clear" in weather_main:
            weather_animation = load_local_lottie("animations/sun.json")

        else:
            weather_animation = None

        if weather_animation:
            st_lottie(weather_animation, height=180, key=f"{city}_anim")
        else:
            st.write("☀️ No animation available")

        col1, col2 = st.columns(2)

        with col1:
            weather_card("Temperature", f"{data['main']['temp']} °C", "🌡️", "#ff512f, #f09819")

        with col2:
            weather_card("Sky Condition", condition, "☁️", "#2193b0, #6dd5ed")

        st.markdown(
            f"""
            <div style="
            padding: 15px;
            border-radius: 12px;
            background-color: #1e1e1e;
            color: white;
            margin-top: 10px;
            ">
            <h4> AI Insight</h4>
            <p>The weather in <b>{city}</b> is currently <b>{temp_state}</b> with <b>{condition}</b>. Plan your day accordingly for best comfort.</p>
            </div>
            """, unsafe_allow_html=True)
        
        temps = []
        times = []

        if not forecast_data.get("list"):
            st.warning("Forecast data not available")
            st.stop()
        
        for item in forecast_data["list"][:6]:
            temps.append(item["main"]["temp"])
            times.append(item["dt_txt"][11:16])
            
        df = pd.DataFrame({"Time": times, "Temperature": temps})
            
        st.markdown("###  Hourly Temperature Trend")
        st.caption("Next 6 time intervals forecast")

        fig = px.line(df, x="Time", y="Temperature", markers=True, title=" Temperature Trend (Next Hours)")
        fig.update_layout(xaxis_title="Time", yaxis_title="Temperature (°C)", title_x=0.2)
        
        st.plotly_chart(fig, use_container_width=True)

        if data:
            st.success("Weather data loaded!")
            st.markdown("###  Weather Dashboard")

            col1, col2, col3 = st.columns(3)

            with col1:
                weather_card("Temperature", f"{data['main']['temp']} °C", "🌡️", "#ff9966, #ff5e62")

            with col2:
                weather_card("Humidity", f"{data['main']['humidity']} %", "💧", "#56ccf2, #2f80ed")

            with col3:
                weather_card("Pressure", f"{data['main']['pressure']} hPa", "🧭", "#43cea2, #185a9d")

            st.markdown("### Extra Weather Info")

            weather_card("Feels Like", f"{data['main'].get('feels_like', temp)} °C", "🥵", "#834d9b, #d04ed6")

            st.subheader("Current Condition")

            icon_code = data["weather"][0]["icon"]
            icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
            st.image(icon_url, width=100)

            st.write(data["weather"][0]["description"].title())
            st.write(f"Wind Speed: {data['wind']['speed']} m/s")

            st.markdown("###  5-Day Forecast")
            st.caption("Daily overview of upcoming weather conditions")

            forecast_list = forecast_data["list"]

            cols = st.columns(5)

            for i in range(5):
                if len(forecast_list) > i*8:
                    item = forecast_list[i*8]
                with cols[i]:
                    st.metric(label=item["dt_txt"][:10], value=f"{item['main']['temp']} °C")
                    st.write( item["weather"][0]["description"].title())
        else:
            st.error("City not found.")
