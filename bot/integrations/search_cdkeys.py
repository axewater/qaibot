import sys
import json
import logging
import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
try:
    from .chrome_webdriver import init_driver
except ImportError:
    from chrome_webdriver import init_driver

def fetch_game_details(game_name):
    # Prepare the search URL
    search_url = f"https://www.cdkeys.com/#q={game_name.replace(' ', '%20')}"

    # Send the request
    driver = init_driver()
    logging.basicConfig(level=logging.INFO)
    logging.info(f"Fetching data from: {search_url}")
    try:
        driver.get(search_url)
        time.sleep(3)  # Allow time for the page to load
        results = driver.find_elements(By.CSS_SELECTOR, 'ol.ais-InfiniteHits-list > li.ais-InfiniteHits-item')
        logging.info(f"Found {len(results)} results")

        games_data = []
        for idx, result in enumerate(results, 1):
            game_title = result.find_element(By.CSS_SELECTOR, 'h3[itemprop="name"]').text.strip()
            price = result.find_element(By.CSS_SELECTOR, 'span[itemprop="lowPrice"]').text.strip()
            thumbnail_url = result.find_element(By.CSS_SELECTOR, 'img[itemprop="image"]').get_attribute('src')
            detail_url = result.find_element(By.CSS_SELECTOR, 'div.result-thumbnail > a').get_attribute('href')

            games_data.append({
                'game_title': game_title,
                'price': price,
                'thumbnail_url': thumbnail_url,
                'detail_url': detail_url
            })
            logging.info(f"Extracted details for game {idx} including detail URL")
    except NoSuchElementException as e:
        logging.error(f"Failed to extract details for one of the games: {e}")
    finally:
        driver.quit()

    return games_data

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <game_name>")
        return

    game_name = ' '.join(sys.argv[1:])
    print("Searching for:", game_name)
    game_details = fetch_game_details(game_name)
    if game_details:
        print(json.dumps(game_details, indent=4))
    else:
        print("No results found")

if __name__ == "__main__":
    main()
