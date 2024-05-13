import argparse
import pandas as pd
import requests_cache
from retry_requests import retry
import openmeteo_requests
from .weather_api_vars import fetch_weather_data
import json

def serialize_weather_response(response):
    """ Custom serialization for WeatherApiResponse objects. """
    if hasattr(response, '_tab'):
        # Assuming '_tab' is a flatbuffers table containing the response data.
        # This needs to be adjusted based on the actual structure and content of '_tab'.
        data = {
            'Latitude': response.Latitude(),
            'Longitude': response.Longitude(),
            'Elevation': response.Elevation(),
            'Timezone': response.Timezone().decode('utf-8'),
            'UtcOffsetSeconds': response.UtcOffsetSeconds(),
            'CurrentWeather': {
                'Time': response.Current().Time(),
                'Temperature': response.Current().Variables(0).Value(),
                'Humidity': response.Current().Variables(1).Value(),
                'Precipitation': response.Current().Variables(2).Value(),
                'Rain': response.Current().Variables(3).Value(),
                'WeatherCode': response.Current().Variables(4).Value(),
                'WindSpeed': response.Current().Variables(5).Value(),
                'WindDirection': response.Current().Variables(6).Value()
            }
        }
        # Handling nested attributes and lists
        if hasattr(response, 'Hourly'):
            hourly_forecasts = []
            for i in range(response.HourlyLength()):
                hourly = response.Hourly(i)
                hourly_forecasts.append({
                    'Time': hourly.Time(),
                    'Temperature': hourly.Variables(0).Value(),
                    'Humidity': hourly.Variables(1).Value()
                })
            data['HourlyForecasts'] = hourly_forecasts

        if hasattr(response, 'Daily'):
            daily_forecasts = []
            for i in range(response.DailyLength()):
                daily = response.Daily(i)
                daily_forecasts.append({
                    'Date': daily.Date(),
                    'MaxTemperature': daily.Variables(0).Value(),
                    'MinTemperature': daily.Variables(1).Value(),
                    'PrecipitationProbability': daily.Variables(2).Value()
                })
            data['DailyForecasts'] = daily_forecasts
        return data
    else:
        return {}

def parse_arguments():
    parser = argparse.ArgumentParser(description='Fetch and display weather data using the Open-Meteo API.')
    parser.add_argument('-lat', '--latitude', type=float, required=True, help='Latitude of the location')
    parser.add_argument('-lon', '--longitude', type=float, required=True, help='Longitude of the location')
    parser.add_argument('--when', type=str, required=True, choices=['now', 'tomorrow', 'week'], help='Time of the weather forecast ("now", "tomorrow", or "week")')
    parser.add_argument('--output-format', type=str, default='json', choices=['json', 'table'], help='Output format of the weather data')
    return parser.parse_args()

def setup_api_client():
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    return openmeteo_requests.Client(session=retry_session)

def format_weather_data(response, forecast_time, output_format):
    result = ""
    # print("Raw API Response:", response)
    # Print detailed attributes of the response object
    # print("Inspecting attributes of the response object:")
    attributes = dir(response)
    for attr in attributes:
        if not attr.startswith('__') and not callable(getattr(response, attr)):
            print(f"{attr}: {getattr(response, attr)}")

    if output_format == 'json':
        try:
            serialized_data = serialize_weather_response(response)
            result = json.dumps(serialized_data, indent=4)
        except TypeError as e:
            print("Error serializing object to JSON:", e)
        return result

    print(f"Coordinates: {response.Latitude()}°N, {response.Longitude()}°E")
    print(f"Elevation: {response.Elevation()} m asl")
    print(f"Timezone: {response.Timezone()} ({response.TimezoneAbbreviation()})")
    print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()} s")

    if forecast_time == 'now':
        current = response.Current()
        print(f"Current time {current.Time()}")
        print(f"Current temperature_2m {current.Variables(0).Value()}")
        print(f"Current relative_humidity_2m {current.Variables(1).Value()}")
        print(f"Current precipitation {current.Variables(2).Value()}")
        print(f"Current rain {current.Variables(3).Value()}")
        print(f"Current weather_code {current.Variables(4).Value()}")
        print(f"Current wind_speed_10m {current.Variables(5).Value()}")
        print(f"Current wind_direction_10m {current.Variables(6).Value()}")

    if forecast_time == 'tomorrow':
        if response.Hourly() is not None:
            hourly = response.Hourly()
            hourly_data = {
                "date": pd.date_range(
                    start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                    end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                    freq=pd.Timedelta(seconds=hourly.Interval()),
                    inclusive="left"
                ),
                "temperature_2m": hourly.Variables(0).ValuesAsNumpy(),
                "precipitation_probability": hourly.Variables(1).ValuesAsNumpy()
            }
            df = pd.DataFrame(data=hourly_data)
            print(df)

    if forecast_time == 'week':
        if response.Daily() is not None:
            daily = response.Daily()
            daily_data = {
                "date": pd.date_range(
                    start=pd.to_datetime(daily.Time(), unit="s", utc=True),
                    end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
                    freq=pd.Timedelta(seconds=daily.Interval()),
                    inclusive="left"
                ),
                "weather_code": daily.Variables(0).ValuesAsNumpy(),
                "temperature_2m_max": daily.Variables(1).ValuesAsNumpy(),
                "temperature_2m_min": daily.Variables(2).ValuesAsNumpy(),
                "precipitation_probability_max": daily.Variables(3).ValuesAsNumpy()
            }
            daily_df = pd.DataFrame(data=daily_data)
            print(daily_df)

def run():
    args = parse_arguments()
    client = setup_api_client()
    response = fetch_weather_data(client, args.latitude, args.longitude, args.when)
    result = format_weather_data(response, args.when, args.output_format)
    print(result)

if __name__ == "__main__":
    run()
