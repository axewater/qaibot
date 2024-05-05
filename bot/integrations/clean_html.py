# bot/integrations/clean_html.py
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def clean_html(content):
    soup = BeautifulSoup(content, 'html.parser')

    # Find all <a> tags and clean their href attributes and data-tracking
    for a_tag in soup.find_all('a'):
        # Clean data-tracking attribute
        if a_tag.has_attr('data-tracking'):
            a_tag['data-tracking'] = 'XXX'
        
        # Remove query parameters from href attribute
        if a_tag.has_attr('href'):
            href = a_tag['href']
            clean_href = href.split('?')[0]  # Keep only the part before the '?'
            a_tag['href'] = clean_href

    return str(soup)

def fetch_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raises HTTPError for bad responses
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        sys.exit(1)

def read_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: The file {file_path} does not exist.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        sys.exit(1)

def save_to_file(content, output_file):
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"Processed HTML has been saved to {output_file}")
    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")
        sys.exit(1)

def validate_url(url):
    parsed = urlparse(url)
    return all([parsed.scheme, parsed.netloc]) and parsed.scheme in ['http', 'https']

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python clean_html.py <input_file_or_url> <output_file>")
        print("       <input_file_or_url> can be a local file path or a valid HTTP/HTTPS URL.")
        print("       <output_file> is the file path where the cleaned HTML will be saved.")
        sys.exit(1)

    input_source = sys.argv[1]
    output_filename = sys.argv[2]

    if validate_url(input_source):
        print(f"Fetching HTML content from URL: {input_source}")
        html_content = fetch_url(input_source)
    else:
        print(f"Reading HTML content from file: {input_source}")
        html_content = read_file(input_source)

    cleaned_html = clean_html(html_content)
    save_to_file(cleaned_html, output_filename)

