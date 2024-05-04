import json
import logging
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
try:
    from .chrome_webdriver import init_driver
except ImportError:
    from chrome_webdriver import init_driver

# Setup basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_cookies(driver, path_to_cookie_file):
    with open(path_to_cookie_file, 'r') as file:
        cookies = json.load(file)
        for cookie in cookies:
            # Adjust the sameSite attribute to a valid value if necessary
            if 'sameSite' in cookie:
                if cookie['sameSite'].lower() in ['no_restriction', 'unspecified']:
                    cookie['sameSite'] = 'None'  # 'None' should be set explicitly where cross-site cookies are allowed
                else:
                    cookie['sameSite'] = 'Lax'  # Default to 'Lax' if not set to 'Strict' or 'None'
            driver.add_cookie(cookie)


def scrape_iptorrents(search_query):
    base_url = "https://www.iptorrents.com/t?q="
    search_url = f"{base_url}{search_query.replace(' ', '+')}"

    driver = init_driver()
    driver.get("https://www.iptorrents.com")  # Load the website to set initial cookies

    # Load the cookies for authentication
    load_cookies(driver, "./bot/integrations/cookie_iptorrents.json")

    logging.info(f"Fetching URL: {search_url}")
    try:
        driver.get(search_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "torrents")))
        time.sleep(2)  # Allow page to fully load
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        table = soup.find('table', {'id': 'torrents'})
        results = []
        
        for row in table.find('tbody').find_all('tr'):
            cols = row.find_all('td')
            if not cols:
                continue

            result = {
                'Type': cols[0].find('img')['alt'] if cols[0].find('img') else 'No type',
                'Name': cols[1].text.strip(),
                'Size': cols[5].text.strip(),
                'Snatches': cols[6].text.strip(),
                'Seeders': cols[7].text.strip(),
                'Leechers': cols[8].text.strip(),
                'Download Link': cols[3].find('a')['href'] if cols[3].find('a') else 'No link'
            }
            results.append(result)
            logging.info(f"Found result: {result}")

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
    if len(sys.argv) != 2:
        logging.error("Usage: python search_iptorrents.py \"<search query>\"")
        sys.exit(1)

    search_query = sys.argv[1]
    logging.info(f"Searching for '{search_query}' on IPTorrents...")
    items = scrape_iptorrents(search_query)
    if items is None:
        print("Failed to retrieve or parse items.")
    else:
        items_json = json.dumps(items, indent=4)
        print(items_json)
