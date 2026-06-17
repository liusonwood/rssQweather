import os
import re
import unicodedata
import requests
import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom
from email.utils import format_datetime
import sys


def rfc822_now():
    """Returns the current UTC time as an RFC 2822 / RSS 2.0 compliant date string.

    Using email.utils.format_datetime guarantees a locale-independent,
    spec-compliant date (e.g. "Tue, 19 May 2026 23:53:02 +0000").
    """
    return format_datetime(datetime.datetime.now(datetime.timezone.utc))

# Configuration
# QWeather API Host for weather endpoints.
# Users must provide their unique API Host from the QWeather Console.
API_HOST = os.environ.get("QWEATHER_HOST")
# GeoAPI Host used to resolve the configured city into a Location ID.
# The default works for most accounts; override only if QWeather provides a dedicated host.
GEOAPI_HOST = os.environ.get("QWEATHER_GEOAPI_HOST") or "geoapi.qweather.com"
# Which city to publish. Accepts a city name (e.g. "Shanghai", "北京"), a QWeather
# Location ID (e.g. "101020100"), an Adcode, or "lon,lat" coordinates.
# Defaults to Shanghai so the project keeps working without any extra configuration.
CITY = (os.environ.get("CITY") or "Shanghai").strip()
RSS_FILENAME = "weather.xml"
MAX_ITEMS = 30  # Keep at most this many items; oldest entries are pruned


def slugify(text):
    """Turns an arbitrary city name into a safe slug for use in GUIDs and URLs.

    Non-ASCII characters are transliterated where possible (e.g. "北京" -> "bei-jing"
    when an English name is passed in, or "" when nothing transliterates), and any
    remaining non alphanumeric characters collapse into single hyphens. Returns an
    empty string (never a placeholder) so callers can apply their own fallback.
    """
    if not text:
        return ""
    # Normalize unicode so accented letters split into base + diacritic, which we strip.
    normalized = unicodedata.normalize("NFKD", str(text))
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    # Lowercase and replace runs of non-alphanumeric chars with a single hyphen.
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_only.lower()).strip("-")
    return slug


def _request_json(host, path, params, what):
    """Shared GET helper with consistent error handling for all QWeather endpoints.

    `what` is a short label used in error messages (e.g. "weather", "geo lookup").
    Returns the parsed JSON body on success and exits the process on any failure.
    """
    url = f"https://{host}{path}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Encoding": "gzip"  # Explicitly request gzip as per docs
    }
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code != 200:
            print(f"HTTP Error ({what}): {response.status_code}")
            print(f"Response Body: {response.text}")
            sys.exit(1)

        data = response.json()
        if data.get("code") != "200":
            print(f"Error from API ({what}): {data.get('code')} - {data.get('msg', 'Unknown error')}")
            sys.exit(1)
        return data
    except requests.exceptions.RequestException as e:
        print(f"Network error ({what}): {e}")
        sys.exit(1)


def resolve_location(api_key):
    """Resolves the configured CITY into a (location_id, display_name) pair.

    Uses the QWeather GeoAPI City Lookup, which accepts a city name, Location ID,
    Adcode, or "lon,lat" coordinates. The first match is returned so the feed
    always points at exactly one city. Exits with a clear message if no match.
    """
    data = _request_json(
        GEOAPI_HOST,
        "/v2/city/lookup",
        {"location": CITY, "key": api_key, "lang": "en", "number": 1},
        "geo lookup",
    )
    locations = data.get("location") or []
    if not locations:
        print(f"Error: Could not resolve city '{CITY}' via GeoAPI.")
        sys.exit(1)
    first = locations[0]
    return first.get("id"), first.get("name", CITY)


def get_weather_forecast(api_key, location_id):
    """Fetches weather data from QWeather API."""
    if not API_HOST:
        print("Error: QWEATHER_HOST environment variable not set.")
        sys.exit(1)

    data = _request_json(
        API_HOST,
        "/v7/weather/3d",
        {"location": location_id, "key": api_key, "lang": "en"},
        "weather",
    )
    return data["daily"]

def generate_rss(daily_forecast, city_name, location_id=None):
    """Generates an RSS 2.0 XML file from the forecast data, appending new data."""

    # Prefer the readable city name; if it cannot be slugified to ASCII (rare for
    # non-Latin names), fall back to the always-numeric Location ID so GUIDs stay
    # unique and valid instead of collapsing into a generic "city" prefix.
    city_slug = slugify(city_name) or slugify(location_id or "")

    # Register Atom namespace
    ET.register_namespace('atom', "http://www.w3.org/2005/Atom")

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
        f"<strong>Condition (Day):</strong> {text_day} (Icon: {icon_day})<br/>"
        f"<strong>Condition (Night):</strong> {text_night} (Icon: {icon_night})<br/>"
        f"<strong>Temperature:</strong> {temp_min}°C to {temp_max}°C<br/>"
        f"<strong>Precipitation:</strong> {precip} mm<br/>"
        f"<strong>Cloud Cover:</strong> {cloud}%<br/>"
        
        f"<br/>"
        
        f"<strong>Wind (Day):</strong> {wind_dir_day} ({wind_360_day}°), Scale {wind_scale_day}, Speed {wind_speed_day} km/h<br/>"
        f"<strong>Wind (Night):</strong> {wind_dir_night} ({wind_360_night}°), Scale {wind_scale_night}, Speed {wind_speed_night} km/h<br/>"
        
        f"<br/>"
        
        f"<strong>Humidity:</strong> {humidity}%<br/>"
        f"<strong>Visibility:</strong> {vis} km<br/>"
        f"<strong>Sun:</strong> Rise {sunrise}, Set {sunset}<br/>"
        f"<strong>Moon:</strong> Rise {moonrise}, Set {moonset} (Phase: {moon_phase},{moon_phase_icon})<br/>"
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
            ET.SubElement(channel, "title").text = f"{city_name} Weather Forecast"
            ET.SubElement(channel, "link").text = f"https://github.com/liusonwood/rssqweather#{date_str}" # Update if needed
            ET.SubElement(channel, "description").text = f"Daily weather forecast for {city_name} via QWeather."
    else:
        rss = ET.Element("rss", version="2.0")
        channel = ET.SubElement(rss, "channel")
        ET.SubElement(channel, "title").text = f"{city_name} Weather Forecast"
        ET.SubElement(channel, "link").text = f"https://github.com/liusonwood/rssqweather#{date_str}" # Update if needed
        ET.SubElement(channel, "description").text = f"Daily weather forecast for {city_name} via QWeather."

    # Add atom:link (required for RSS validation)
    atom_ns = "http://www.w3.org/2005/Atom"
    atom_link_url = "https://raw.githubusercontent.com/liusonwood/rssqweather/main/weather.xml"
    
    # Check if link exists
    atom_link = None
    for child in channel.findall(f"{{{atom_ns}}}link"):
        if child.get("rel") == "self":
            atom_link = child
            break
            
    if atom_link is None:
        atom_link = ET.SubElement(channel, f"{{{atom_ns}}}link")
        atom_link.set("rel", "self")
        atom_link.set("type", "application/rss+xml")
    
    # Always update the href
    atom_link.set("href", atom_link_url)

    # Sync channel metadata to the currently configured city so switching CITY
    # updates the feed title/description even when the file already exists.
    channel_title = channel.find("title")
    if channel_title is None:
        channel_title = ET.SubElement(channel, "title")
    channel_title.text = f"{city_name} Weather Forecast"

    channel_desc = channel.find("description")
    if channel_desc is None:
        channel_desc = ET.SubElement(channel, "description")
    channel_desc.text = f"Daily weather forecast for {city_name} via QWeather."

    # Update Last Build Date
    last_build_date = channel.find("lastBuildDate")
    if last_build_date is None:
        last_build_date = ET.SubElement(channel, "lastBuildDate")
    last_build_date.text = rfc822_now()

    # Check for duplicate item (by GUID)
    guid_text = f"{city_slug}-weather-{date_str}"
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
    ET.SubElement(item, "link").text = f"https://github.com/liusonwood/rssqweather#{date_str}"
    ET.SubElement(item, "description").text = description
    ET.SubElement(item, "guid", isPermaLink="false").text = guid_text
    ET.SubElement(item, "pubDate").text = rfc822_now()
    
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

    # Prune oldest items when the feed exceeds the configured limit.
    # New items are inserted at the top, so items are ordered newest -> oldest.
    items = channel.findall("item")
    excess = len(items) - MAX_ITEMS
    if excess > 0:
        for old_item in items[-excess:]:
            channel.remove(old_item)
        print(f"Pruned {excess} old item(s) to keep at most {MAX_ITEMS} entries.")

    # Pretty print XML
    xml_str = minidom.parseString(ET.tostring(rss)).toprettyxml(indent="  ")
    
    # Remove empty lines generated by minidom
    xml_str = "\n".join([line for line in xml_str.split('\n') if line.strip()])
    
    with open(RSS_FILENAME, "w", encoding="utf-8") as f:
        f.write(xml_str)
        
    print(f"Successfully generated {RSS_FILENAME} for {city_name}.")

def main():
    api_key = os.environ.get("QWEATHER_KEY")
    if not api_key:
        print("Error: QWEATHER_KEY environment variable not set.")
        sys.exit(1)

    # Resolve the configured city into a QWeather Location ID. Falls back to
    # Shanghai when CITY is not set, so no extra configuration is required.
    location_id, city_name = resolve_location(api_key)
    print(f"Resolved city '{CITY}' -> {city_name} (Location ID: {location_id})")

    forecast_data = get_weather_forecast(api_key, location_id)
    generate_rss(forecast_data, city_name, location_id)

if __name__ == "__main__":
    main()
