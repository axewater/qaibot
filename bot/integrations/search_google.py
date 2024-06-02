# bot/integrations/search_google.py

import logging
import sys
import os
import argparse
import json

# Dynamically add the bot directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from ..config import GOOGLE_API_KEY, GOOGLE_CX
except ImportError:
    from config import GOOGLE_API_KEY, GOOGLE_CX
    
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def perform_web_search(query, start_index=1, max_results=5):
    """Performs a web search using the Google Search API and returns URLs up to max_results."""
    urls = []
    try:
        # Strip any leading or trailing quotes from the query
        cleaned_query = query.strip('\'"')
        
        logging.info(f"perform_web_search: Performing web search for: {cleaned_query} with start index: {start_index} and max results: {max_results}")
        logging.info(f"perform_web_search: Using GOOGLE_API_KEY: {GOOGLE_API_KEY} and GOOGLE_CX: {GOOGLE_CX}")
        service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        total_results_fetched = 0

        while total_results_fetched < max_results:
            request_body = {
                'q': cleaned_query,
                'cx': GOOGLE_CX,
                'num': min(10, max_results - total_results_fetched),
                'start': start_index
            }
            logging.info(f"perform_web_search: Sending request to Google API with body: {json.dumps(request_body, indent=2)}")
            
            try:
                res = service.cse().list(**request_body).execute()
            except HttpError as e:
                error_details = json.loads(e.content.decode())
                error_reason = error_details.get('error', {}).get('errors', [{}])[0].get('reason', 'Unknown error')
                error_message = f"Google Search API returned an error: {error_reason}"
                logging.error(error_message)
                return error_message

            logging.info(f"perform_web_search: Received response from Google API: {json.dumps(res, indent=2)}")
            
            items = res.get("items", [])
            if not items:
                logging.info(f"perform_web_search: No search results found for: {cleaned_query}")
                break

            for item in items:
                if total_results_fetched >= max_results:
                    break
                urls.append(item["link"])
                total_results_fetched += 1

            start_index += len(items)

        logging.info(f"perform_web_search: Found this number of URLS: {len(urls)}")
        return urls

    except (Exception, ValueError) as e:
        logging.error(f"Failed to perform web search using Google Search API: {str(e)}")
        return str(e)


def main():
    parser = argparse.ArgumentParser(description="Perform a web search using the Google Search API.")
    parser.add_argument('query', type=str, help='The search query.')
    parser.add_argument('--start_index', type=int, default=1, help='The starting index for search results.')
    parser.add_argument('--max_results', type=int, default=5, help='The maximum number of results to fetch.')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    
    urls = perform_web_search(args.query, args.start_index, args.max_results)
    if isinstance(urls, str):
        print(f"Error: {urls}")
    else:
        for url in urls:
            print(url)


if __name__ == "__main__":
    main()
