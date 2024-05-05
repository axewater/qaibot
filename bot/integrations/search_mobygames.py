# bot/integrations/search_mobygames.py
import requests, json, sys, urllib.parse, logging
from ..config import MOBYGAMES_API_KEY

def search_mobygames(game_name):
    encoded_game_name = urllib.parse.quote(game_name)  # Ensure the game name is URL-encoded
    logging.info(f"search_mobygames: Called with game name '{game_name}'")
    url = f"https://api.mobygames.com/v1/games?title={encoded_game_name}&api_key={MOBYGAMES_API_KEY}?format=normal"
    
    try:
        logging.info(f"search_mobygames: Searching for '{game_name}' using MobyGames API...")
        response = requests.get(url)
        response.raise_for_status()  # Raises HTTPError for bad responses
        data = response.json()
        logging.info(f"Data: {data}")
        return data
    except requests.RequestException as e:
        logging.error(f"search_mobygames: Error occurred while fetching data: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python search_mobygames.py \"<game_name>\"")
        sys.exit(1)

    game_name = " ".join(sys.argv[1:])
    results = search_mobygames(game_name)
    if results is None:
        print("Failed to retrieve data.")
    else:
        results_json = json.dumps(results, indent=4)
        print(results_json)
