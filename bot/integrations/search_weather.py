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

class WeatherSearchError(Exception):
    pass

def main(location_name=None, report_type='now'):
    if location_name is None:
        raise WeatherSearchError("Usage: python search_weather.py <location_name> <report_type>")

    latitude, longitude = get_coordinates(location_name, os.getenv('GOOGLE_MAPS_API_KEY'))
    if latitude is None or longitude is None:
        raise WeatherSearchError("Could not get coordinates for the location.")

    sys.argv = ['weather_api.py', '-lat', str(latitude), '-lon', str(longitude), '--when', report_type, '--output-format', 'table']
    fetch_weather()

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise WeatherSearchError("Usage: python search_weather.py <location_name> <report_type>")
    main(sys.argv[1], sys.argv[2])
