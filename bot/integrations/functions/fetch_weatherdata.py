# bot/integrations/functions/weather/fetch_weatherdata.py

def fetch_weather_data(client, latitude, longitude, forecast_time):
    url = "https://api.open-meteo.com/v1/forecast"
    if forecast_time == 'now':
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": ["temperature_2m", "relative_humidity_2m", "precipitation", "rain", "weather_code", "wind_speed_10m", "wind_direction_10m"],
            "timezone": "auto"
        }
    elif forecast_time == 'tomorrow':
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": ["temperature_2m", "precipitation_probability"],
            "daily": "weather_code",
            "timezone": "auto",
            "forecast_days": 1
        }
    elif forecast_time == 'week':
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "precipitation_probability_max"],
            "timezone": "auto"
        }
    responses = client.weather_api(url, params=params)
    return responses[0]  # Assuming single location response