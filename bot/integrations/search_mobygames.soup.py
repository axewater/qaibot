import requests
from bs4 import BeautifulSoup
import json
import sys
import logging

def search_mobygames(game_name):
    base_url = "https://www.mobygames.com/search/?q="
    search_url = base_url + requests.utils.quote(game_name)
    try:
        response = requests.get(search_url)
        print(f"Searching for '{game_name}' on MobyGames...")
        response.raise_for_status()  # Raises HTTPError for bad responses
    except requests.RequestException as e:
        logging.error(f"Network or HTTP error occurred while fetching data for {game_name}: {e}")
        return None  # Return None to indicate failure

    try:
        soup = BeautifulSoup(response.content, "html.parser")
        results = []
        print("Parsing HTML content...")
        for item in soup.select("table.table.mb tbody tr"):
            print(f"Parsing result for {game_name}...")
            game_element = item.select_one("b > a")
            print(f"Parsing date for {game_name}...")
            date_element = item.select_one("span.text-muted")
            print(f"Parsing platforms for {game_name}...")
            platforms_element = item.select("small > small.text-muted")
            print(f"Parsing link for {game_name}...")

            if game_element and date_element:
                game_name = game_element.text.strip()
                print(f"stripped game name {game_name}...")
                game_link = "https://www.mobygames.com" + game_element['href']
                print(f"game link {game_link}...")
                release_date = date_element.text.strip().strip('()')
                print(f"release date {release_date}...")
                platforms = [plat.text.strip('(),') for plat in platforms_element]
                print(f"platforms {platforms}...")

                results.append({
                    "game_name": game_name,
                    "release_date": release_date,
                    "platforms": platforms,
                    "link": game_link
                })
                print(f"Results: {results}")
            else:
                logging.warning(f"Missing essential elements in result for {game_name}")

        if not results:
            logging.info(f"No valid results found for {game_name}")
            return None  # Return None to indicate no valid results

        return results
    except Exception as e:
        logging.error(f"Error parsing HTML content for {game_name}: {e}")
        return None  # Return None to indicate parsing failure

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python search_mobygames.py \"<game_name>\"")
        sys.exit(1)

    game_name = " ".join(sys.argv[1:])
    try:
        print(f"Searching for '{game_name}' on MobyGames...")
        results = search_mobygames(game_name)
        if results is None:
            print("Failed to retrieve or parse search results.")
        else:
            results_json = json.dumps(results, indent=4)
            print(results_json)
    except Exception as e:
        print(f"Error: {e}")