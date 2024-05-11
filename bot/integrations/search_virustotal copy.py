import os
import sys
import argparse
import json
import requests
from tabulate import tabulate

# Dynamically add the bot directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from bot.config import VIRUSTOTAL_API_KEY
except ImportError:
    from config import VIRUSTOTAL_API_KEY


def is_valid_input(input_string):
    # Simple checks to determine if the input could be a URL, domain, IP, or hash
    if any(char in input_string for char in "/:"):
        return "url"
    elif len(input_string.split('.')) > 1:
        return "domain"
    elif all(c.isdigit() or c == '.' for c in input_string) and input_string.count('.') == 3:
        return "ip"
    elif len(input_string) in [32, 40, 64]:  # Common lengths for MD5, SHA-1, SHA-256
        return "hash"
    return None

def query_virustotal(query, input_type):
    url = f"https://www.virustotal.com/api/v3/{input_type}s/{query}"
    headers = {
        "x-apikey": VIRUSTOTAL_API_KEY
    }
    response = requests.get(url, headers=headers)
    return response.json()

def format_output(data, output_format):
    if output_format == 'json':
        return json.dumps(data, indent=4)
    elif output_format == 'table':
        if 'data' in data:
            headers = data['data'][0].keys()
            rows = [x.values() for x in data['data']]
            return tabulate(rows, headers=headers)
        return "No data available"
    return "Invalid format"

def main():
    parser = argparse.ArgumentParser(description='Search URLs, domains, IPs, and hashes in VirusTotal.')
    parser.add_argument('query', help='The query string (URL, domain, IP, or hash)')
    parser.add_argument('--output', choices=['json', 'table'], default='json', help='Output format')
    args = parser.parse_args()

    input_type = is_valid_input(args.query)
    if not input_type:
        print("Invalid input. Please enter a valid URL, domain, IP address, or hash.")
        return

    result = query_virustotal(args.query, input_type)
    print(format_output(result, args.output))

if __name__ == "__main__":
    main()
