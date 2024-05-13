#!/usr/bin/env python3
import argparse
import pandas as pd
import requests_cache
from retry_requests import retry
import openmeteo_requests

def parse_arguments():
    parser = argparse.ArgumentParser(description='Fetch and display weather data using the Open-Meteo API.')
    parser.add_argument('-lat', '--latitude', type=float, required=True, help='Latitude of the location')
    parser.add_argument('-lon', '--longitude', type=float, required=True, help='Longitude of the location')
    parser.add_argument('-v', '--variables', type=str, default='temperature_2m', help='Weather variables to retrieve (comma-separated)')
    return parser.parse_args()

def setup_api_client():
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    return openmeteo_requests.Client(session=retry_session)

def fetch_weather_data(client, latitude, longitude, variables):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": variables
    }
    responses = client.weather_api(url, params=params)
    return responses[0]  # Assuming single location response

def display_weather_data(response):
    print(f"Coordinates: {response.Latitude()}°N, {response.Longitude()}°E")
    print(f"Elevation: {response.Elevation()} m asl")
    print(f"Timezone: {response.Timezone()} ({response.TimezoneAbbreviation()})")
    print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()} s")

    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        ),
        "temperature_2m": hourly_temperature_2m
    }
    df = pd.DataFrame(data=hourly_data)
    print(df)

def main():
    args = parse_arguments()
    client = setup_api_client()
    response = fetch_weather_data(client, args.latitude, args.longitude, args.variables)
    display_weather_data(response)

if __name__ == "__main__":
    main()
