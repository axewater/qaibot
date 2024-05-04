import sys
import json
import logging
import time
from selenium.webdriver.common.by import By
from .chrome_webdriver import init_driver

def scrape_marktplaats_items(search_query):
    base_url = "https://www.marktplaats.nl/q/"
    url = f"{base_url}{search_query.replace(' ', '+')}/"

    driver = init_driver()
    logging.info(f"Fetching URL: {url}")
    try:
        driver.get(url)
        time.sleep(1)  # Allow some time for the page to load
        results = []
        items = driver.find_elements(By.CSS_SELECTOR, ".hz-Listing.hz-Listing--list-item")

        logging.info(f"Found {len(items)} items on the page.")
        for item in items:
            title_element = item.find_element(By.CSS_SELECTOR, ".hz-Listing-title")
            price_element = item.find_element(By.CSS_SELECTOR, ".hz-Listing-price")

            title = title_element.text.strip() if title_element else "No title found"
            price = price_element.text.strip() if price_element else "Bieden"

            logging.info(f"Item found: Title: {title}, Price: {price}")
            results.append({
                "title": title,
                "price": price
            })

        if not results:
            logging.info("No valid results found.")
            return None
    except Exception as e:
        logging.error(f"Error while processing the page: {e}")
        return None
    finally:
        driver.quit()

    return results

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    search_query = " ".join(sys.argv[1:])
    logging.info(f"Searching for '{search_query}' on Marktplaats...")
    items = scrape_marktplaats_items(search_query)
    if items is None:
        print("Failed to retrieve or parse items.")
    else:
        items_json = json.dumps(items, indent=4)
        print(items_json)
