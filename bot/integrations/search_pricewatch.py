# bot/integrations/search_pricewatch.py
import requests
from bs4 import BeautifulSoup
import json, sys, logging

cookies = {
    "SSLB": "1",
    "tbb": "false",
}

def search_tweakers_pricewatch(component_name):
    component_name = component_name.replace("\"", "")
    logging.info(f"search_tweakers_pricewatch: Called with component name '{component_name}'")
    base_url = "https://tweakers.net/pricewatch/"
    search_url = base_url + "zoeken/?keyword=" + component_name
    try:
        response = requests.get(search_url, cookies=cookies)
        response.raise_for_status()  # Raises HTTPError for bad responses
    except requests.RequestException as e:
        logging.error(f"Network or HTTP error occurred while fetching data for {component_name}: {e}")
        return None  # Return None to indicate failure

    try:
        logging.info(f"search_tweakers_pricewatch: Souping HTML content...")
        soup = BeautifulSoup(response.content, "html.parser")
        results = []
        for item in soup.select("table.listing tr"):
            name_element = item.select_one(".editionName")
            price_element = item.select_one("td.price-score > p.price > a")
            
            if name_element and price_element:
                name = name_element.text.strip()
                price = price_element.text.strip()
                link = name_element["href"] if "href" in name_element.attrs else "#"
                
                if name and price and link != "#":
                    results.append({
                        "name": name,
                        "price": price,
                        "link": link,
                    })
                else:
                    logging.warning(f"search_tweakers_pricewatch: Skipping incomplete result for {component_name}: Name={name}, Price={price}, Link={link}")
            else:
                logging.warning(f"search_tweakers_pricewatch: Missing essential elements in result for {component_name}")

        if not results:
            logging.info(f"search_tweakers_pricewatch: No valid results found for {component_name}")
            return None  # Return None to indicate no valid results

        return results
    except Exception as e:
        logging.error(f"search_tweakers_pricewatch: Error parsing HTML content for {component_name}: {e}")
        return None  # Return None to indicate parsing failure

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tweakers_pricewatch.py \"<component_name>\"")
        sys.exit(1)

    component_name = " ".join(sys.argv[1:])
    try:
        print(f"Searching for '{component_name}' on Tweakers Pricewatch...")
        results = search_tweakers_pricewatch(component_name)
        if results is None:
            print("Failed to retrieve or parse search results.")
        else:
            results_json = json.dumps(results, indent=4)
            print(results_json)
    except Exception as e:
        print(f"Error: {e}")
