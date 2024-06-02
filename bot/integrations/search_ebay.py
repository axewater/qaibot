import os, sys
import json
import argparse
from ebaysdk.finding import Connection

# Dynamically add the bot directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from ..config import EBAY_APP_ID as APP_ID, EBAY_DEV_ID as DEV_ID, EBAY_CERT_ID as CERT_ID
except ImportError:
    from config import EBAY_APP_ID as APP_ID, EBAY_DEV_ID as DEV_ID, EBAY_CERT_ID as CERT_ID

def search_ebay(query, max_results=10):
    try:
        api = Connection(appid=APP_ID, config_file=None)
        response = api.execute('findItemsByKeywords', {'keywords': query})

        items = response.reply.searchResult.item[:max_results]

        results = []
        for item in items:
            item_info = {
                'name': item.title,
                'category': item.primaryCategory.categoryName,
                'shipto': item.shippingInfo.shipToLocations,
                'price': item.sellingStatus.currentPrice.value,
                'item_url': item.viewItemURL,
                'image_url': item.galleryURL
            }
            results.append(item_info)

        return json.dumps(results, indent=2)

    except Exception as e:
        print(f"Error: {str(e)}")
        return None


def main():
    parser = argparse.ArgumentParser(description='Search for items on eBay')
    parser.add_argument('query', help='The item you want to search for on eBay')
    parser.add_argument('-m', '--max', type=int, default=10, help='Maximum number of results to return (default: 10)')
    args = parser.parse_args()

    results = search_ebay(args.query, args.max)
    if results:
        print(results)
    else:
        print("No results found.")


def display_help():
    print("Usage: python script.py [-h] [-m MAX] query")
    print("\nSearch for items on eBay")
    print("\npositional arguments:")
    print("  query                 The item you want to search for on eBay")
    print("\noptional arguments:")
    print("  -h, --help            Show this help message and exit")
    print("  -m MAX, --max MAX     Maximum number of results to return (default: 10)")


if __name__ == '__main__':
    if len(os.sys.argv) == 1 or '-h' in os.sys.argv or '--help' in os.sys.argv:
        display_help()
    else:
        main()