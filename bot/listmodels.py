import os
import requests
import config

# Retrieve the API key from the configuration
api_key = config.OPENAI_API_KEY

# Set up the API headers
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_key}'
}

# Make the API request
response = requests.get('https://api.openai.com/v1/models', headers=headers)

# Print the results
if response.status_code == 200:
    models = response.json()['data']
    print('Available models:')
    for model in models:
        print(f'- {model["id"]}')
else:
    print(f'Error: {response.status_code}')
