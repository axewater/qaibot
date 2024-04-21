# bot/integrations/tweakers_pricewatch.py
import requests
from bs4 import BeautifulSoup
import json  # For JSON output
import sys

cookies = {
    "SSLB": "1",
    "tbb": "false",
}


# Function to search component prices on Tweakers Pricewatch
def search_tweakers_pricewatch(component_name):
    base_url = "https://tweakers.net/pricewatch/"
    search_url = base_url + "zoeken/?keyword=" + component_name
    response = requests.get(search_url, cookies=cookies)

    if response.status_code != 200:
        raise Exception("Failed to fetch data from Tweakers Pricewatch.")

    soup = BeautifulSoup(response.content, "html.parser")

    results = []
    for item in soup.select("table.listing tr"):
        name_element = item.select_one(".editionName")
        price_element = item.select_one("td.price-score > p.price > a")
        
        if name_element and price_element:
            name = name_element.text.strip()
            price = price_element.text.strip()
            
            # Extract the product link from 'href'
            link = name_element["href"] if "href" in name_element.attrs else "#"
            full_link = f"https://tweakers.net{link}" 
            
            results.append({
                "name": name,
                "price": price,
                "link": full_link,
            })
        else:
            pass

    return results

# Command-line interface to use the function from the command line
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tweakers_pricewatch.py \"<component_name>\"")
        sys.exit(1)

    component_name = " ".join(sys.argv[1:])  # Join all arguments to handle spaces in the name
    try:
        print(f"Searching for '{component_name}' on Tweakers Pricewatch...")
        results = search_tweakers_pricewatch(component_name)
        
        # Output results in JSON format
        results_json = json.dumps(results, indent=4)  # Serialize to JSON with indentation
        print(results_json)  # Print JSON output
    except Exception as e:
        print(f"Error: {e}")
