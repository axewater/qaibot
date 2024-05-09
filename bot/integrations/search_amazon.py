import requests
import logging
import argparse
import json
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def search_amazon(query):
    """
    Search Amazon for a given query and return the top results.
    """
    if not query:
        logging.error("search_amazon: No search query provided.")
        return []
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"

    try:
        logging.info(f"search_amazon: Searching Amazon for '{query}'...")
        # Placeholder for URL and headers, adjust as necessary based on Amazon's API or scraping method
        url = f"https://www.amazon.com/s?k={query.replace(' ', '+')}"
        headers = {
            "User-Agent": user_agent,
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Connection": "keep-alive",
            "Referer": "https://www.google.com",
            "Cache-Control": "no-cache",
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        logging.info("search_amazon: Request successful, processing results...")

        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        items = soup.find_all('div', {'data-component-type': 's-search-result'})
        for item in items:
            asin = item.get('data-asin')
            title_element = item.find('span', {'class': 'a-size-base-plus'})
            title = title_element.text.strip() if title_element else 'No title'
            image_element = item.find('img', {'class': 's-image'})
            image = image_element['src'] if image_element else 'No image'
            price_element = item.find('span', {'class': 'a-price'})
            price = price_element.find('span', {'class': 'a-offscreen'}).text if price_element and price_element.find('span', {'class': 'a-offscreen'}) else 'No price'
            rating_element = item.find('i', {'class': 'a-icon-star-small'})
            rating = rating_element.find('span', {'class': 'a-icon-alt'}).text if rating_element and rating_element.find('span', {'class': 'a-icon-alt'}) else 'No rating'
            num_ratings_element = item.find('span', {'class': 'a-size-base'})
            num_ratings = num_ratings_element.text if num_ratings_element else 'No ratings'
            delivery_date_element = item.find('span', {'class': 'a-color-base'})
            delivery_date = delivery_date_element.text if delivery_date_element else 'No delivery date'
            link_element = item.find('a', {'class': 'a-link-normal'}, href=True)
            link = f"https://www.amazon.com{link_element['href']}" if link_element else 'No link'
            results.append({
                'ASIN': asin,
                'Title': title,
                'Image': image,
                'Price': price,
                'Rating': rating,
                'Number of Ratings': num_ratings,
                'Delivery Date': delivery_date,
                'Link': link
            })

        logging.info(f"search_amazon: Found {len(results)} results.")
        return json.dumps(results)

    except requests.RequestException as e:
        logging.error(f"search_amazon: Request failed: {e}")
        return json.dumps({'error': str(e)})
    except Exception as e:
        logging.error(f"search_amazon: An error occurred: {e}")
        return json.dumps({'error': str(e)})

def main():
    parser = argparse.ArgumentParser(description='Search Amazon for a given query and return the top results.')
    parser.add_argument('query', type=str, nargs='?', help='The search query string')
    args = parser.parse_args()

    if not args.query:
        parser.print_help()
        return

    results_json = search_amazon(args.query)
    print(results_json)

if __name__ == "__main__":
    main()
