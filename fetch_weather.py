import os
import requests
import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom
import sys

# Configuration
# QWeather API Endpoint
# Users must provide their unique API Host from the QWeather Console
API_HOST = os.environ.get("QWEATHER_HOST")
LOCATION_ID = "101020100" # Shanghai
RSS_FILENAME = "weather.xml"

def get_weather_forecast(api_key):
    """Fetches weather data from QWeather API."""
    if not API_HOST:
        print("Error: QWEATHER_HOST environment variable not set.")
        sys.exit(1)
        
    # Construct the full URL using the dynamic host
    url = f"https://{API_HOST}/v7/weather/3d"
    
    params = {
        "location": LOCATION_ID,
        "key": api_key,
        "lang": "en"
    }
    
    # Adding a User-Agent is a best practice to avoid 403 errors
    headers = {
        "User-Agent": "WeatherRSSBot/1.0 (GitHub Actions)",
        "Accept-Encoding": "gzip" # Explicitly request gzip as per docs
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        
        # Check for HTTP errors
        if response.status_code != 200:
            print(f"HTTP Error: {response.status_code}")
            print(f"Response Body: {response.text}")
            sys.exit(1)

        data = response.json()
        
        if data.get("code") != "200":
            print(f"Error from API: {data.get('code')} - {data.get('msg', 'Unknown error')}")
            sys.exit(1)
            
        return data["daily"]
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        sys.exit(1)

def generate_rss(daily_forecast):
    """Generates an RSS 2.0 XML file from the forecast data."""
    
    # We want tomorrow's weather. 
    # daily_forecast[0] is today, daily_forecast[1] is tomorrow.
    if len(daily_forecast) < 2:
        print("Error: Insufficient forecast data received.")
        sys.exit(1)
        
    tomorrow = daily_forecast[1]
    
    # Parse data
    date_str = tomorrow["fxDate"] 
    text_day = tomorrow["textDay"]
    text_night = tomorrow["textNight"]
    temp_max = tomorrow["tempMax"]
    temp_min = tomorrow["tempMin"]
    humidity = tomorrow["humidity"]
    wind_dir = tomorrow["windDirDay"]
    wind_scale = tomorrow["windScaleDay"]
    uv_index = tomorrow["uvIndex"]
    
    # Format Title and Description
    title = f"{date_str}: {text_day}, {temp_min}°C - {temp_max}°C"
    
    description = (
        f"<strong>Date:</strong> {date_str}<br/>"
        f"<strong>Day:</strong> {text_day}<br/>"
        f"<strong>Night:</strong> {text_night}<br/>"
        f"<strong>Temperature:</strong> {temp_min}°C to {temp_max}°C<br/>"
        f"<strong>Humidity:</strong> {humidity}%<br/>"
        f"<strong>Wind:</strong> {wind_dir} (Scale: {wind_scale})<br/>"
        f"<strong>UV Index:</strong> {uv_index}"
    )

    # Build XML
    rss = ET.Element("rss", version="2.0")
    channel = ET.SubElement(rss, "channel")
    
    ET.SubElement(channel, "title").text = "Shanghai Weather Forecast"
    ET.SubElement(channel, "link").text = "https://github.com/liusonwood/github-rss-weather" # Update if needed
    ET.SubElement(channel, "description").text = "Daily weather forecast for Shanghai via QWeather."
    ET.SubElement(channel, "lastBuildDate").text = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
    
    item = ET.SubElement(channel, "item")
    ET.SubElement(item, "title").text = title
    ET.SubElement(item, "description").text = description
    ET.SubElement(item, "guid").text = f"shanghai-weather-{date_str}"
    ET.SubElement(item, "pubDate").text = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

    # Pretty print XML
    xml_str = minidom.parseString(ET.tostring(rss)).toprettyxml(indent="  ")
    
    with open(RSS_FILENAME, "w", encoding="utf-8") as f:
        f.write(xml_str)
        
    print(f"Successfully generated {RSS_FILENAME}")

def main():
    api_key = os.environ.get("QWEATHER_KEY")
    if not api_key:
        print("Error: QWEATHER_KEY environment variable not set.")
        sys.exit(1)
        
    forecast_data = get_weather_forecast(api_key)
    generate_rss(forecast_data)

if __name__ == "__main__":
    main()
