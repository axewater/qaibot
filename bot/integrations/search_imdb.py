import requests
from bs4 import BeautifulSoup
import logging
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def search_imdb(query):
    """
    Search IMDB for a given query and return the top results.
    """
    if not query:
        logging.error("No search query provided.")
        return []

    try:
        logging.info(f"Searching IMDb for '{query}'...")
        # Construct the search URL
        url = f"https://www.imdb.com/find?q={query.replace(' ', '+')}&s=tt&ttype=ft&ref_=fn_ft"

        # Headers to mimic a regular browser request
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Connection": "keep-alive",
            "Referer": "https://www.google.com",
            "Cache-Control": "no-cache",
        }

        # Send HTTP request
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        logging.info("Request successful, processing results...")

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        search_results = soup.find_all('li', class_='find-result-item')

        if not search_results:
            logging.warning("No results found.")
            return []

        # Extract data from each result
        results = []
        for result in search_results:
            title_element = result.find('a', class_='ipc-metadata-list-summary-item__t')
            year = result.find('span', class_='ipc-metadata-list-summary-item__li')
            actor_list = result.find_all('span', class_='ipc-metadata-list-summary-item__li')[1:]
            actors = ', '.join([actor.get_text(strip=True) for actor in actor_list])

            if title_element:
                title = title_element.get_text(strip=True)
                link = "https://www.imdb.com" + title_element['href']
                year_text = year.get_text(strip=True) if year else "N/A"
                results.append({
                    'title': title,
                    'link': link,
                    'year': year_text,
                    'actors': actors
                })

        logging.info(f"Found {len(results)} results.")
        return results

    except requests.RequestException as e:
        logging.error(f"Request failed: {e}")
        return []
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return []

def main():
    parser = argparse.ArgumentParser(description='Search IMDb for a given query and return the top results including title, link, year, and main actors.')
    parser.add_argument('query', type=str, nargs='?', help='The search query string')
    args = parser.parse_args()

    if not args.query:
        parser.print_help()
        return

    results = search_imdb(args.query)
    if results:
        for result in results:
            print(f"Title: {result['title']}, Year: {result['year']}, Actors: {result['actors']}, Link: {result['link']}")
    else:
        print("No results found or an error occurred.")

if __name__ == "__main__":
    main()
