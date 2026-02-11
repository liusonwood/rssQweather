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
    """Generates an RSS 2.0 XML file from the forecast data, appending new data."""
    
    # We want tomorrow's weather. 
    # daily_forecast[0] is today, daily_forecast[1] is tomorrow.
    if len(daily_forecast) < 2:
        print("Error: Insufficient forecast data received.")
        sys.exit(1)
        
    tomorrow = daily_forecast[1]
    
    # Parse data
    date_str = tomorrow.get("fxDate", "N/A")
    
    # Astronomical
    sunrise = tomorrow.get("sunrise", "N/A")
    sunset = tomorrow.get("sunset", "N/A")
    moonrise = tomorrow.get("moonrise", "N/A")
    moonset = tomorrow.get("moonset", "N/A")
    moon_phase = tomorrow.get("moonPhase", "N/A")
    moon_phase_icon = tomorrow.get("moonPhaseIcon", "N/A")
    
    # Temperature
    temp_max = tomorrow.get("tempMax", "N/A")
    temp_min = tomorrow.get("tempMin", "N/A")
    
    # Day Condition
    icon_day = tomorrow.get("iconDay", "N/A")
    text_day = tomorrow.get("textDay", "N/A")
    wind_360_day = tomorrow.get("wind360Day", "N/A")
    wind_dir_day = tomorrow.get("windDirDay", "N/A")
    wind_scale_day = tomorrow.get("windScaleDay", "N/A")
    wind_speed_day = tomorrow.get("windSpeedDay", "N/A")
    
    # Night Condition
    icon_night = tomorrow.get("iconNight", "N/A")
    text_night = tomorrow.get("textNight", "N/A")
    wind_360_night = tomorrow.get("wind360Night", "N/A")
    wind_dir_night = tomorrow.get("windDirNight", "N/A")
    wind_scale_night = tomorrow.get("windScaleNight", "N/A")
    wind_speed_night = tomorrow.get("windSpeedNight", "N/A")
    
    # Other
    humidity = tomorrow.get("humidity", "N/A")
    precip = tomorrow.get("precip", "N/A")
    pressure = tomorrow.get("pressure", "N/A")
    vis = tomorrow.get("vis", "N/A")
    cloud = tomorrow.get("cloud", "N/A")
    uv_index = tomorrow.get("uvIndex", "N/A")
    
    # Format Title
    title = f"{date_str}: {text_day}, {temp_min}°C - {temp_max}°C"
    
    # Format Description
    description = (
        f"<strong>Date:</strong> {date_str}<br/>"
        f"<strong>Condition (Day):</strong> {text_day} (Icon: {icon_day})<br/>"
        f"<strong>Condition (Night):</strong> {text_night} (Icon: {icon_night})<br/>"
        f"<strong>Temperature:</strong> {temp_min}°C to {temp_max}°C<br/>"
        f"<strong>Sun:</strong> Rise {sunrise}, Set {sunset}<br/>"
        f"<strong>Moon:</strong> Rise {moonrise}, Set {moonset} (Phase: {moon_phase})<br/>"
        f"<strong>Wind (Day):</strong> {wind_dir_day} ({wind_360_day}°), Scale {wind_scale_day}, Speed {wind_speed_day} km/h<br/>"
        f"<strong>Wind (Night):</strong> {wind_dir_night} ({wind_360_night}°), Scale {wind_scale_night}, Speed {wind_speed_night} km/h<br/>"
        f"<strong>Humidity:</strong> {humidity}%<br/>"
        f"<strong>Precipitation:</strong> {precip} mm<br/>"
        f"<strong>Pressure:</strong> {pressure} hPa<br/>"
        f"<strong>Visibility:</strong> {vis} km<br/>"
        f"<strong>Cloud Cover:</strong> {cloud}%<br/>"
        f"<strong>UV Index:</strong> {uv_index}"
    )

    # Load existing RSS or create new
    if os.path.exists(RSS_FILENAME):
        try:
            tree = ET.parse(RSS_FILENAME)
            rss = tree.getroot()
            channel = rss.find("channel")
            if channel is None:
                raise ValueError("Invalid RSS: Missing channel")
        except (ET.ParseError, ValueError):
            print("Warning: Corrupt or invalid RSS file. Creating new.")
            rss = ET.Element("rss", version="2.0")
            channel = ET.SubElement(rss, "channel")
            ET.SubElement(channel, "title").text = "Shanghai Weather Forecast"
            ET.SubElement(channel, "link").text = "https://github.com/liusonwood/github-rss-weather" # Update if needed
            ET.SubElement(channel, "description").text = "Daily weather forecast for Shanghai via QWeather."
    else:
        rss = ET.Element("rss", version="2.0")
        channel = ET.SubElement(rss, "channel")
        ET.SubElement(channel, "title").text = "Shanghai Weather Forecast"
        ET.SubElement(channel, "link").text = "https://github.com/liusonwood/github-rss-weather" # Update if needed
        ET.SubElement(channel, "description").text = "Daily weather forecast for Shanghai via QWeather."

    # Update Last Build Date
    last_build_date = channel.find("lastBuildDate")
    if last_build_date is None:
        last_build_date = ET.SubElement(channel, "lastBuildDate")
    last_build_date.text = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

    # Check for duplicate item (by GUID)
    guid_text = f"shanghai-weather-{date_str}"
    existing_item = None
    for item in channel.findall("item"):
        guid = item.find("guid")
        if guid is not None and guid.text == guid_text:
            existing_item = item
            break
    
    if existing_item:
        channel.remove(existing_item)
        
    # Create new item
    item = ET.Element("item")
    ET.SubElement(item, "title").text = title
    ET.SubElement(item, "link").text = "https://github.com/liusonwood/github-rss-weather"
    ET.SubElement(item, "description").text = description
    ET.SubElement(item, "guid").text = guid_text
    ET.SubElement(item, "pubDate").text = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
    
    # Insert at the beginning of items (after channel metadata)
    # Find index of first 'item'
    first_item_index = -1
    for i, child in enumerate(channel):
        if child.tag == 'item':
            first_item_index = i
            break
    
    if first_item_index != -1:
        channel.insert(first_item_index, item)
    else:
        channel.append(item)

    # Pretty print XML
    xml_str = minidom.parseString(ET.tostring(rss)).toprettyxml(indent="  ")
    
    # Remove empty lines generated by minidom
    xml_str = "\n".join([line for line in xml_str.split('\n') if line.strip()])
    
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
