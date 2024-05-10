# bot/integrations/google_search.py

import argparse
import json
import logging
import sys

sys.path.append('c:/scripts/qaibot/bot')

parser = argparse.ArgumentParser(description='Perform a Google web search.')
parser.add_argument('query', type=str, nargs='?', help='Search query string')
args = parser.parse_args()

if not args.query:
    parser.print_help()
    sys.exit(1)

try:
    from ..config import GOOGLE_API_KEY, GOOGLE_CX
except ImportError:
    from config import GOOGLE_API_KEY, GOOGLE_CX

from googleapiclient.discovery import build
import googleapiclient.errors


def perform_web_search(query, start_index=1, max_results=5):
    """Performs a web search using the Google Search API and returns URLs up to max_results."""
    urls = []
    try:
        logging.info(f"perform_web_search: Performing web search for: {query}")
        service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY, cache_discovery=False)
        total_results_fetched = 0

        while total_results_fetched < max_results:
            res = service.cse().list(
                q=query, cx=GOOGLE_CX, num=min(10, max_results - total_results_fetched), start=start_index
            ).execute()
            logging.info(f"perform_web_search: Received search results from Google API")
            items = res.get("items", [])
            if not items:
                break

            for item in items:
                if total_results_fetched >= max_results:
                    break
                urls.append(item["link"])
                total_results_fetched += 1

            start_index += len(items)

        logging.info(f"perform_web_search: Received URLs from search results: {urls}")
        return urls

    except googleapiclient.errors.HttpError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
    except Exception as e:
        logging.error(f"Failed to perform web search using Google Search API: {e}")
        return []


if __name__ == "__main__":
    results = perform_web_search(args.query)
    print(results)
