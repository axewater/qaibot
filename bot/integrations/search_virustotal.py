import os
import sys
import argparse
import json
import requests
import logging
import re
from tabulate import tabulate

# Dynamically add the bot directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from bot.config import VIRUSTOTAL_API_KEY
except ImportError:
    from config import VIRUSTOTAL_API_KEY

def is_valid_url(input_string):
    print(f"is_valid_url: Validating URL: {input_string}")
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    if re.match(url_pattern, input_string):
        print(f"is_valid_url: URL is valid: {input_string}")
        return True
    return False

def is_valid_ip(input_string):
    print(f"is_valid_ip: Validating IP address: {input_string}")
    ip_pattern = r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'
    if re.match(ip_pattern, input_string):
        print(f"is_valid_ip: IP address is valid: {input_string}")
        return True
    return False

def is_valid_hash(input_string):
    print(f"is_valid_hash: Validating file hash: {input_string}")
    hash_pattern = r'^[a-fA-F0-9]{32}$|^[a-fA-F0-9]{40}$|^[a-fA-F0-9]{64}$'
    if re.match(hash_pattern, input_string):
        print(f"is_valid_hash: File hash is valid: {input_string}")
        return True
    return False

def is_valid_domain(input_string):
    print(f"is_valid_domain: Validating domain: {input_string}")
    domain_pattern = r'^[\w\-\.]+\.\w+$'
    if re.match(domain_pattern, input_string):
        print(f"is_valid_domain: Domain is valid: {input_string}")
        return True
    return False

def query_domain(domain):
    print(f"query_domain: Querying VirusTotal for '{domain}'")
    url = f"https://www.virustotal.com/api/v3/domains/{domain}"
    headers = {
        "x-apikey": VIRUSTOTAL_API_KEY
    }
    response = requests.get(url, headers=headers)
    print(f"query_domain: API response code: {response.status_code}")
    return response.json()

def query_url(url):
    print(f"query_url: Querying VirusTotal for URL: '{url}'")
    url = "https://www.virustotal.com/api/v3/urls"
    headers = {
        "x-apikey": VIRUSTOTAL_API_KEY
    }
    response = requests.post(url, headers=headers, data={"url": url})
    print(f"query_url: API response code: {response.status_code}")
    return response.json()

def query_ip(ip):
    print(f"query_ip: Querying VirusTotal for IP address: '{ip}'")
    url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
    headers = {
        "x-apikey": VIRUSTOTAL_API_KEY
    }
    response = requests.get(url, headers=headers)
    print(f"query_ip: API response code: {response.status_code}")
    return response.json()

def query_file_hash(file_hash):
    print(f"query_file_hash: Querying VirusTotal for file hash: '{file_hash}'")
    url = f"https://www.virustotal.com/api/v3/files/{file_hash}"
    headers = {
        "x-apikey": VIRUSTOTAL_API_KEY
    }
    response = requests.get(url, headers=headers)
    print(f"query_file_hash: API response code: {response.status_code}")
    return response.json()

def process_ip_data(data):
    attributes = data['data']['attributes']
    ip_address_info = {
        "IP Address": data['data']['id'],
        "Network": attributes.get('network', 'Unknown'),
        "Continent": attributes.get('continent', 'Unknown'),
        "Reputation": attributes.get('reputation', 0),
        "Last Modification Date": attributes.get('last_modification_date', 'Unknown'),
        "Crowdsourced Context": [
            {
                "Timestamp": context['timestamp'],
                "Details": context['details'],
                "Title": context['title'],
                "Severity": context['severity'],
                "Source": context['source']
            } for context in attributes.get('crowdsourced_context', [])
        ],
        "Analysis Results": {
            engine['engine_name']: {
                "Category": engine['category'],
                "Result": engine['result']
            } for engine in attributes['last_analysis_results'].values()
        },
        "Whois Information": attributes.get('whois', 'Unknown')
    }
    return ip_address_info

def process_domain_data(data):
    attributes = data['data']['attributes']
    domain_info = {
        "Domain ID": data['data']['id'],
        "Last DNS Records": attributes.get('last_dns_records', []),
        "Last Modification Date": attributes.get('last_modification_date', 'Unknown'),
        "Last HTTPS Certificate Date": attributes.get('last_https_certificate_date', 'Unknown'),
        "Tags": attributes.get('tags', []),
        "Creation Date": attributes.get('creation_date', 'Unknown'),
        "Last Analysis Stats": attributes.get('last_analysis_stats', {}),
        "Whois Information": attributes.get('whois', 'Unknown'),
        "Last DNS Records Date": attributes.get('last_dns_records_date', 'Unknown'),
        "Total Votes": attributes.get('total_votes', {}),
        "Last Analysis Date": attributes.get('last_analysis_date', 'Unknown'),
        "Last Update Date": attributes.get('last_update_date', 'Unknown'),
        "Reputation": attributes.get('reputation', 0),
        "Registrar": attributes.get('registrar', 'Unknown'),
        "TLD": attributes.get('tld', 'Unknown'),
        "Last Analysis Results": {engine['engine_name']: {
            "Method": engine['method'],
            "Category": engine['category'],
            "Result": engine['result']
        } for engine in attributes['last_analysis_results'].values()},
        "Popularity Ranks": attributes.get('popularity_ranks', {}),
        "Last HTTPS Certificate": attributes.get('last_https_certificate', {}),
        "JARM": attributes.get('jarm', 'Unknown'),
        "Categories": attributes.get('categories', {})
    }
    return domain_info

def process_url_data(data):
    if 'links' not in data['data']:
        return {"error": "Missing *links* in URL analysis response"}
    report_url = data['data']['links'].get('self', 'No report URL available')
    return {"Report URL": report_url}

def process_file_hash_data(data):
    attributes = data['data']['attributes']
    analysis_results = attributes.get('last_analysis_results', {})
    analysis_summary = {
        "md5": attributes.get('md5', 'Unknown'),
        "sha1": attributes.get('sha1', 'Unknown'),
        "sha256": attributes.get('sha256', 'Unknown'),
        "reputation": attributes.get('reputation', 0),
        "type_description": attributes.get('type_description', 'Unknown'),
        "malicious_votes": attributes['last_analysis_stats'].get('malicious', 0),
        "undetected_votes": attributes['last_analysis_stats'].get('undetected', 0),
        "Antivirus Results": {k: v['result'] for k, v in analysis_results.items() if v['result']}
    }
    return analysis_summary

def format_output(data, output_format):
    if output_format == 'json':
        
        processed_data = data
        return json.dumps(processed_data, indent=4)
    elif output_format == 'table':
        if 'data' in data:
            headers = data['data'][0].keys()
            rows = [x.values() for x in data['data']]
            return tabulate(rows, headers=headers)
        return "No data available"
    return "Invalid format"

def main():
    parser = argparse.ArgumentParser(description='Search domains in VirusTotal.')
    parser.add_argument('query', help='The query to search')
    parser.add_argument('--type', choices=['domain', 'url', 'ip', 'hash'], default='domain', help='Type of query')
    parser.add_argument('--output', choices=['json', 'table'], default='json', help='Output format')
    args = parser.parse_args()

    if args.type == 'domain':
        if not is_valid_domain(args.query):
            print("Invalid domain. Please enter a valid domain.")
            return
        result = query_domain(args.query)
    elif args.type == 'url':
        if not is_valid_url(args.query):
            print("Invalid URL. Please enter a valid URL.")
            return
        result = query_url(args.query)
    elif args.type == 'ip':
        if not is_valid_ip(args.query):
            print("Invalid IP address. Please enter a valid IP address.")
            return
        result = query_ip(args.query)
    elif args.type == 'hash':
        if not is_valid_hash(args.query):
            print("Invalid file hash. Please enter a valid file hash.")
            return
        result = query_file_hash(args.query)
    else:
        print("Invalid query type. Please enter a valid query type.")
        return

    print(format_output(result, args.output))

if __name__ == "__main__":
    main()
