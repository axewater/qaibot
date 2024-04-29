import requests
from bs4 import BeautifulSoup
import json
import sys
import logging
import urllib.parse

def scrape_marktplaats_items(search_query):
    base_url = "https://www.marktplaats.nl/q/"
    # Properly encode the search query to handle spaces and special characters
    query_encoded = urllib.parse.quote_plus(search_query)
    url = base_url + query_encoded + "/"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises HTTPError for bad responses
    except requests.RequestException as e:
        logging.error(f"Network or HTTP error occurred while fetching data for {search_query}: {e}")
        return None  # Return None to indicate failure

    try:
        soup = BeautifulSoup(response.content, "html.parser")
        results = []
        ## print(soup.prettify())
        for item in soup.select(".hz-Listing.hz-Listing--list-item"):
            print(f"item: {item}")
            title_element = item.select_one(".hz-Listing-title")
            print(f"title_element: {title_element}")
            price_element = item.select_one(".hz-Listing-price")
            print(f"price_element: {price_element}")

            title = title_element.text.strip() if title_element else "No title found"
            price = price_element.text.strip() if price_element else "Bieden"

            results.append({
                "title": title,
                "price": price
            })

        if not results:
            logging.info(f"No valid results found for {search_query}")
            return None  # Return None to indicate no valid results

        return results
    except Exception as e:
        logging.error(f"Error parsing HTML content for {search_query}: {e}")
        return None  # Return None to indicate parsing failure

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) < 2:
        print("Usage: python marktplaats_scraper.py \"<search_query>\"")
        sys.exit(1)

    search_query = " ".join(sys.argv[1:])
    print(f"Searching for '{search_query}' on Marktplaats...")
    items = scrape_marktplaats_items(search_query)
    if items is None:
        print("Failed to retrieve or parse items.")
    else:
        items_json = json.dumps(items, indent=4)
        print(items_json)
