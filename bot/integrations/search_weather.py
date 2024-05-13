import sys
import os
import json

sys.path.append('/bot/integrations/functions')  # Ensure the functions directory is in the path

try:
    from functions.loc2co import get_coordinates
except ImportError:
    from .functions.loc2co import get_coordinates

try:
    from functions.weather_api import run as fetch_weather
except ImportError:
    from .functions.weather_api import run as fetch_weather

def main():
    if len(sys.argv) != 2:
        print("Usage: python search_weather.py <location_name>")
        sys.exit(1)

    location_name = sys.argv[1]
    latitude, longitude = get_coordinates(location_name, os.getenv('GOOGLE_MAPS_API_KEY'))
    if latitude is None or longitude is None:
        print("Could not get coordinates for the location.")
        sys.exit(1)

    # Simulating the command line arguments for weather_api.run()
    sys.argv = ['weather_api.py', '-lat', str(latitude), '-lon', str(longitude), '--when', 'now', '--output-format', 'table']
    fetch_weather()

if __name__ == "__main__":
    main()
