import argparse
import requests
import os, sys
import pandas as pd
from openmeteo_requests import Client
import json
from retry_requests import retry
import requests_cache
import logging

# Dynamically add the bot directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from config import GOOGLE_MAPS_API_KEY
except ImportError:
    from ..config import GOOGLE_MAPS_API_KEY

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def get_coordinates(location_name, api_key):
    """Fetch latitude and longitude for a given location name using Google Maps Geocoding API."""
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": location_name,
        "key": api_key
    }
    response = requests.get(base_url, params=params)
    logging.debug(f"Requesting coordinates for {location_name} with params: {params}")
    if response.status_code == 200:
        json_response = response.json()
        logging.debug(f"Received response: {json_response}")
        if json_response['status'] == 'OK':
            geometry = json_response['results'][0]['geometry']['location']
            return geometry['lat'], geometry['lng']
    return None, None

def main():
    parser = argparse.ArgumentParser(description="Fetch weather predictions based on location name.")
    parser.add_argument("--location", type=str, required=True, help="Location name")
    parser.add_argument("--hourly", nargs='+', help="List of hourly weather variables to fetch")
    parser.add_argument("--daily", nargs='+', help="List of daily weather variables to fetch")
    parser.add_argument("--output", choices=["json", "table"], default="json", help="Output format (json or table)")
    args = parser.parse_args()

    logging.debug(f"Starting main function with arguments: {args}")

    google_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    logging.debug(f"Using Google Maps API key: {google_api_key[:6]}...")

    if not google_api_key:
        raise ValueError("Google Maps API key not found in environment variables.")

    # Convert location name to coordinates
    latitude, longitude = get_coordinates(args.location, google_api_key)
    logging.debug(f"Coordinates received: Latitude={latitude}, Longitude={longitude}")
    if latitude is None or longitude is None:
        raise ValueError("Unable to get coordinates for the provided location.")

    # Setup the API client with cache and retry
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    client = Client(session=retry_session)

    # Construct the API parameters
    params = {
        "latitude": latitude,
        "longitude": longitude,
    }
    if args.hourly:
        params["hourly"] = ",".join(args.hourly)
    if args.daily:
        params["daily"] = ",".join(args.daily)
    logging.debug(f"API request parameters: {params}")

    # Fetch the weather data
    try:
        responses = client.weather_api("https://api.open-meteo.com/v1/forecast", params=params)
        response = responses[0]  # Assuming we are interested in the first response
        logging.debug(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
        logging.debug(f"Elevation {response.Elevation()} m asl")
        logging.debug(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
        logging.debug(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")
        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        hourly_data = {"date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        )}
        hourly_data["temperature_2m"] = hourly_temperature_2m
        hourly_dataframe = pd.DataFrame(data=hourly_data)
        logging.debug(f"API response received: {response}")
        if 'error' in response:
            raise ValueError(f"Error from Open Meteo API: {response['error']}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {e}")
        sys.exit(1)
    
    # Handle the output
    if args.output == "json":
        print(json.dumps(response, indent=2))
    else:
        # Process and print data in a table format using pandas
        hourly_data = response.get('hourly', {})
        if hourly_data:
            hourly_df = pd.DataFrame(hourly_data)
            print(hourly_df.to_string(index=False))

if __name__ == "__main__":
    main()
