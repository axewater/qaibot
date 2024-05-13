import argparse
import requests
import os, sys
import json
import logging

# Dynamically add the bot directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from config import GOOGLE_MAPS_API_KEY
except ImportError:
    from ...config import GOOGLE_MAPS_API_KEY

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
    parser = argparse.ArgumentParser(description="Fetch coordinates based on location name.")
    parser.add_argument("--location", type=str, required=True, help="Location name")
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

    # Output the coordinates in JSON format
    coordinates = {"latitude": latitude, "longitude": longitude}
    print(json.dumps(coordinates, indent=2))

if __name__ == "__main__":
    main()
