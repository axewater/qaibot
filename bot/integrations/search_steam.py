import requests
import json
import sys
from tabulate import tabulate

def search_steam(game_name=None, output_format='json'):
    if game_name is None:
        # If no game name is provided, read from command line arguments
        if len(sys.argv) > 1:
            game_name = sys.argv[1]
            output_format = 'json' if '--json' in sys.argv else 'table'
        else:
            print("Usage: search_steam.py <game_name> [--json]")
            return json.dumps({"error": "No game name provided"})
    
    try:
        # Replace spaces with '+' for the URL
        game_name_formatted = game_name.replace(' ', '+')
        response = requests.get(f"https://store.steampowered.com/api/storesearch/?term={game_name_formatted}&cc=US&l=english")

        # Check if the response was successful
        if response.status_code == 200:
            search_results = response.json()
            if output_format == 'table':
                if 'items' in search_results:
                    table = [[item.get('name', 'Not available'), 
                              f"${item.get('price', {}).get('final', 0) / 100:.2f}" if 'price' in item and 'final' in item['price'] else 'Free/Not available']
                             for item in search_results.get('items', [])]
                    print(tabulate(table, headers=['Game Name', 'Price'], tablefmt='grid'))
                else:
                    print("No results found.")
                return
            return json.dumps(search_results)
        else:
            return json.dumps({"error": f"Received response with status code {response.status_code}"})

    except requests.exceptions.RequestException as e:
        return json.dumps({"error": str(e)})

if __name__ == "__main__":
    if len(sys.argv) > 2:
        print(search_steam())
    else:
        # print proper usage information
        print("Usage: search_steam.py <game_name> [--json]")
