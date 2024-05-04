import requests
from bs4 import BeautifulSoup
import json
import sys
import logging

# Setup basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def search_torrents(search_query):
    logging.info(f"Starting search for: {search_query}")

    # Custom headers to mimic a regular browser request
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
    headers = {
        "User-Agent": user_agent,
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Connection": "keep-alive",
        "Referer": "https://www.google.com",
        "Cache-Control": "no-cache",
    }

    # Sanitize and prepare the search query URL
    query_sanitized = search_query.replace(" ", "-").lower()
    first_char = query_sanitized[0]
    search_url = f"https://www.magnetdl.com/{first_char}/{query_sanitized}/"
    logging.info(f"Constructed URL: {search_url}")

    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Failed to retrieve data: {e}")
        return {'error': f"Failed to retrieve data: {e}"}

    logging.info(f"Received response with status code: {response.status_code}")

    # Parse the response using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', class_='download')

    if not table:
        logging.warning("No results found - no table present on the page.")
        return {'error': "No results found"}

    results = []
    rows = table.find_all('tr')[1:]  # Skip header row

    for row in rows:
        columns = row.find_all('td')
        if len(columns) < 8:  # Check if all expected columns are present
            logging.warning("Skipping a row with insufficient data.")
            continue

        seeders = columns[-2].text.strip()
        if seeders == '0':
            logging.info("Skipping torrent with 0 seeders.")
            continue  # Skip torrents with 0 seeders

        magnet_link = columns[0].find('a', href=True)['href'] if columns[0].find('a', href=True) else "No magnet link"
        details_page_url = f"https://www.magnetdl.com{columns[1].find('a', href=True)['href']}" if columns[1].find('a', href=True) else "No detail page"
        
        result = {
            'Download Name': columns[1].get_text(strip=True),
            'Age': columns[2].get_text(strip=True),
            'Type': columns[3].get_text(strip=True),
            'Files': columns[4].get_text(strip=True),
            'Size': columns[5].get_text(strip=True),
            'SE': seeders,
            'LE': columns[-1].get_text(strip=True),
            'Magnet Link': magnet_link,
            'Detail Page URL': details_page_url
        }
        results.append(result)
        if len(results) == 10:  # Limit results to 10 items
            break

    if not results:
        logging.info("No valid torrents found with seeders after processing all rows.")
        return {'error': "No valid torrents found with seeders"}

    return results

if __name__ == "__main__":
    if len(sys.argv) != 2:
        logging.error("Usage: python search_magnetdl.py \"<search query>\"")
        sys.exit(1)

    search_query = sys.argv[1]
    results = search_torrents(search_query)
    print(json.dumps(results, indent=4))
