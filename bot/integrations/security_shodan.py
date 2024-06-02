#!/usr/bin/env python
#
# shodan_search.py
# Search Shodan.io and return the results in JSON format
#
# Author: YourName

import shodan
import sys, os
import json
import argparse

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from ..config import SHODAN_API_KEY
except ImportError:
    from config import SHODAN_API_KEY

# Configuration
API_KEY = SHODAN_API_KEY

def search_shodan(query, facets=None, page=1):
    try:
        # Setup the API
        api = shodan.Shodan(API_KEY)

        # Perform the search
        result = api.search(query, facets=facets, page=page)

        # Return the results as JSON
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})

def host_info(ip, minify=False):
    try:
        # Setup the API
        api = shodan.Shodan(API_KEY)

        # Get host information
        result = api.host(ip, minify=minify)

        # Return the results as JSON
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Search Shodan.io and return the results in JSON format")
    parser.add_argument("query", help="The search query", nargs='?')
    parser.add_argument("-o", "--output", help="Output file to save the results")
    parser.add_argument("-f", "--facets", help="...")  # Facets help information
    parser.add_argument("-p", "--page", type=int, default=1, help="Page number of the search results (default: 1)")
    parser.add_argument("-i", "--ip", help="Get information about a specific IP address")
    parser.add_argument("-m", "--minify", action="store_true", help="Only return open ports and banner information for the specified IP address")
    args = parser.parse_args()

    if args.ip:
        # Get information about a specific IP address
        result = host_info(args.ip, minify=args.minify)
    elif args.query:
        # Perform the search
        facets = args.facets.split(",") if args.facets else None
        result = search_shodan(args.query, facets=facets, page=args.page)
    else:
        parser.print_help()
        return

    # Save the results to a file if the -o flag is provided
    if args.output:
        with open(args.output, 'w') as file:
            file.write(result)
        print(f"Results saved to {args.output}")
    else:
        # Print the results
        print(result)

if __name__ == "__main__":
    main()