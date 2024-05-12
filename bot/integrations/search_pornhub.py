# bot/integrations/search_pornhub.py
# searches pornhub for terms and returns video URLs in JSON format

import json, sys, logging, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup, NavigableString

try:
    from .chrome_webdriver import init_driver
except ImportError:
    from chrome_webdriver import init_driver


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def scrape_pornhub(search_query):
    
    base_url = "https://www.pornhub.com/video"
    search_url = f"{base_url}/search?search={search_query}"

    driver = init_driver()
    driver.get(base_url)  # Load the website to set initial cookies

    try:
        driver.get(search_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "gateway-modal")))
        logging.info("scrape_pornhub: Page loaded successfully, waiting for 1 seconds...")
        time.sleep(1)  # Allow page to load
        logging.info("scrape_iptorrents: Page fully loaded, souping results...")
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        video_list = soup.find('ul', {'id': 'videoSearchResult'})
        results = []

        videos = video_list.find_all('li', class_=lambda x: x and 'pcVideoListItem' in x.split())
        logging.info(f"scrape_pornhub: Found {len(videos)} results using updated class selector")
        for video in videos:
            video_link_element = video.find('a', {'class': 'fade videoPreviewBg linkVideoThumb js-linkVideoThumb img fadeUp'})
            if video_link_element:
                video_link = video_link_element['href']
                title = video_link_element['data-title']
            else:
                video_link = 'URL not found'
                title = 'Title not found'
            
            author_element = video.find('a', {'rel': ''})
            if author_element:
                author = author_element.text
            else:
                author = 'Author not found'
            
            views_element = video.find('span', {'class': 'views'})
            if views_element:
                views = views_element.text
            else:
                views = 'Views not found'
            
            rating_element = video.find('div', {'class': 'value'})
            if rating_element:
                rating = rating_element.text
            else:
                rating = 'Rating not found'
            
            duration_element = video.find('var', {'class': 'duration'})
            if duration_element:
                duration = duration_element.text
            else:
                duration = 'Duration not found'

            result = {
                'Viewing URL': base_url + video_link,
                'Title': title,
                'Author': author,
                'Views': views,
                'Rating': rating,
                'Duration': duration
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
        logging.error("Usage: python search_pornhub.py <search_query>")
        sys.exit(1)
        
    search_query = sys.argv[1]
    logging.info(f"search_pornhub: Initiating scrape for '{search_query}' on PornHub...")
    items = scrape_pornhub(search_query)
    if items is None:
        logging.error("search_pornhub: Failed to retrieve or parse items from PornHub.")
    else:
        items_json = json.dumps(items, indent=4)
        logging.info(f"search_pornhub: Results: {items_json}")
