#!/usr/bin/env python
#
# shodan_search.py
# Search Shodan.io and return the results in JSON format
#
# Author: YourName

import shodan
import sys
import json
import argparse

# Configuration
API_KEY = "YOUR_API_KEY"

def search_shodan(query):
    try:
        # Setup the API
        api = shodan.Shodan(API_KEY)

        # Perform the search
        result = api.search(query)

        # Return the results as JSON
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": str(e)})

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Search Shodan.io and return the results in JSON format")
    parser.add_argument("query", help="The search query")
    args = parser.parse_args()

    # Perform the search
    result = search_shodan(args.query)

    # Print the results
    print(result)

if __name__ == "__main__":
    main()