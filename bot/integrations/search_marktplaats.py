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

def scrape_marktplaats_items(search_query, blacklist):
    base_url = "https://www.marktplaats.nl/q/"
    url = f"{base_url}{search_query.replace(' ', '+')}/"

    driver = init_driver()
    logging.basicConfig(level=logging.INFO)
    logging.info(f"Fetching URL: {url}")
    try:
        driver.get(url)
        time.sleep(2)  # time for the page to load
        results = []
        count = 0
        index = 0
        max_attempts = 30  # Avoid infinite loops, adjust as necessary
        
        while count < 6 and index < max_attempts:
            try:
                item = driver.find_elements(By.CSS_SELECTOR, ".hz-Listing.hz-Listing--list-item")[index]
            except IndexError:
                logging.info("No more items available on the page.")
                break

            title_element = item.find_element(By.CSS_SELECTOR, ".hz-Listing-title")
            price_element = item.find_element(By.CSS_SELECTOR, ".hz-Listing-price")
            link_element = item.find_element(By.CSS_SELECTOR, "a")  # Assuming the link is in the first <a> element
            image_element = item.find_element(By.CSS_SELECTOR, "img") if item.find_elements(By.CSS_SELECTOR, "img") else None
            seller_element = item.find_element(By.CSS_SELECTOR, ".hz-Listing-seller-name")

            title = title_element.text.strip() if title_element else "No title found"
            price = price_element.text.strip() if price_element else "Bieden"
            item_url = link_element.get_attribute('href') if link_element else "URL not found"
            image_url = image_element.get_attribute('src') if image_element else "No image available"
            seller_name = seller_element.text.strip().lower() if seller_element else ""

            index += 1  # Move to the next item
            
            if seller_name in blacklist:
                logging.info(f"Skipping blacklisted seller: {seller_name}")
                continue  # Skip this item and proceed with the next
            
            logging.info(f"Item found: Title: {title}, Price: {price}, URL: {item_url}, Seller: {seller_name}")
            results.append({
                "title": title,
                "price": price,
                "url": item_url,
                "image_url": image_url
            })
            count += 1

        if not results:
            logging.info("No valid results found after filtering blacklisted sellers.")
            return None
    except Exception as e:
        logging.error(f"Error while processing the page: {e}")
        return None
    finally:
        driver.quit()

    return results

if __name__ == "__main__":
    search_query = " ".join(sys.argv[1:])
    logging.info(f"Searching for '{search_query}' on Marktplaats...")
    items = scrape_marktplaats_items(search_query, [])
    if items is None:
        print("Failed to retrieve or parse items.")
    else:
        items_json = json.dumps(items, indent=4)
        print(items_json)
