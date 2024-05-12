import os
import sys
import argparse
import json
import requests
from tabulate import tabulate
import re
import logging

# Dynamically add the bot directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from bot.config import VIRUSTOTAL_API_KEY
except ImportError:
    from config import VIRUSTOTAL_API_KEY

def is_valid_input(input_string):
    logging.info(f"is_valid_input: Validating input: {input_string}")
    url_pattern = r'^https?:\/\/(?:www\.)?[\w\-\.]+(?:\/[\w\-\.\/]*)?$'
    if re.match(url_pattern, input_string):
        logging.info(f"is_valid_input: URL is valid: {input_string}")
        return "url"
    ip_pattern = r'^\d{1,3}(\.\d{1,3}){3}$'
    if re.match(ip_pattern, input_string):
        logging.info(f"is_valid_input: IP is valid: {input_string}")
        return "ip"
    domain_pattern = r'^[\w\-\.]+\.\w+$'
    if re.match(domain_pattern, input_string):
        logging.info(f"is_valid_input: Domain is valid: {input_string}")
        return "domain"
    elif len(input_string) in [32, 40, 64]:
        logging.info(f"is_valid_input: Hash is valid: {input_string}")
        return "hash"
    return None

def query_virustotal(query, input_type):
    logging.info(f"query_virustotal: Querying VirusTotal for '{query}'")
    url = f"https://www.virustotal.com/api/v3/{input_type}s/{query}"
    headers = {
        "x-apikey": VIRUSTOTAL_API_KEY
    }
    response = requests.get(url, headers=headers)
    logging.info(f"query_virustotal: API response: {response.text}")
    return response.json()

def process_data(data):
    # Check if the expected keys are present in the data
    logging.info(f"process_data: Processing data: {data}")
    if 'data' not in data or 'attributes' not in data['data']:
        return {"error": "Missing *data* or *attributes* in API response"}

    attributes = data['data']['attributes']
    logging.info(f"process_data: processing summary...")
    # Initialize summary dictionary with safety checks for each field
    summary = {
        "Domain Information": {
            "Domain": data['data'].get('id', 'Unknown'),
            "Registrar": attributes.get('registrar', 'Unknown'),
            "Reputation": attributes.get('reputation', 0),
            "Creation Date": attributes.get('creation_date', 'Unknown')
        },
        "Security Overview": {
            "Harmless": attributes['last_analysis_stats'].get('harmless', 0),
            "Undetected": attributes['last_analysis_stats'].get('undetected', 0),
            "Malicious": attributes['last_analysis_stats'].get('malicious', 0)
        },
        "DNS Records": [
            {"Type": record['type'], "Value": record['value']}
            for record in attributes.get('last_dns_records', [])
            if record['type'] != 'TXT'
        ]
    }
    logging.info(f"process_data: processing certificate validity...")
    # Check for HTTPS certificate data safely
    certificate_data = attributes.get('last_https_certificate', {}).get('validity', {})
    summary["Certificate Validity"] = {
        "Not Before": certificate_data.get('not_before', 'Unknown'),
        "Not After": certificate_data.get('not_after', 'Unknown')
    }

    return summary

def format_output(data, output_format):
    # logging statements should show progress and counts of objects found
    logging.info(f"format_output: Formatting output to: {output_format}")
    if output_format == 'json':
        processed_data = process_data(data)
        logging.info(f"format_output: returning JSON dump with : {len(processed_data)} number of elements")
        return json.dumps(processed_data, indent=4)
    elif output_format == 'table':
        if 'data' in data:
            headers = data['data'][0].keys()
            rows = [x.values() for x in data['data']]
            logging.info(f"format_output: returning table with : {len(rows)} number of rows")
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

    logging.info(f"virustotal main: input_type: {input_type} and query: {args.query}")
    result = query_virustotal(args.query, input_type)
    print(format_output(result, args.output))

if __name__ == "__main__":
    main()
