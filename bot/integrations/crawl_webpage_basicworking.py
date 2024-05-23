import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import argparse

# Define the user agent and headers
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
headers = {
    "User-Agent": user_agent,
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Connection": "keep-alive",
    "Referer": "https://www.google.com",
    "Cache-Control": "no-cache",
}

# Function to ensure the URL has a scheme
def ensure_url_scheme(url):
    if not urlparse(url).scheme:
        return 'http://' + url
    return url

# Function to get the content of a URL
def get_page_content(url):
    print(f"Fetching content from: {url}")
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Ensure we notice bad responses
    return response.text

# Function to extract relevant text content
def extract_text_content(html_content):
    print("Extracting text content...")
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Heuristic: Find the main content section
    content = soup.find('main') or soup.find('article') or soup.find('body')
    if not content:
        print("No main content found.")
        return ""
    
    text = ' '.join(p.get_text() for p in content.find_all('p'))
    print("Text content extracted.")
    return text[:2000]  # Only the first 2000 characters, roughly 4 pages

# Function to find sub-URLs within the same domain
def find_sub_urls(base_url, html_content, max_sub_urls=10):
    print("Finding sub-URLs...")
    soup = BeautifulSoup(html_content, 'html.parser')
    domain = urlparse(base_url).netloc
    sub_urls = set()
    
    for link in soup.find_all('a', href=True):
        href = link['href']
        full_url = urljoin(base_url, href)
        if urlparse(full_url).netloc == domain:
            sub_urls.add(full_url)
    
    sub_urls = list(sub_urls)
    print(f"Found {len(sub_urls)} sub-URLs.")
    
    # Prioritize sub-URLs (this can be adjusted based on more complex logic)
    prioritized_sub_urls = prioritize_sub_urls(sub_urls)
    
    # Limit to max_sub_urls
    limited_sub_urls = prioritized_sub_urls[:max_sub_urls]
    print(f"Limiting to {len(limited_sub_urls)} sub-URLs.")
    return limited_sub_urls

# Function to prioritize sub-URLs
def prioritize_sub_urls(sub_urls):
    # Example priority: URLs containing certain keywords
    keywords = ['article', 'post', 'blog']
    prioritized_sub_urls = sorted(sub_urls, key=lambda url: any(keyword in url for keyword in keywords), reverse=True)
    return prioritized_sub_urls

# Function to save text content to a file
def save_text_content(base_dir, url, content):
    path = os.path.join(base_dir, urlparse(url).netloc + urlparse(url).path.replace('/', '_') + '.txt')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    print(f"Saving content to: {path}")
    with open(path, 'w', encoding='utf-8') as file:
        file.write(content)
    print("Content saved.")
    return path

# Main function to crawl and summarize
def crawl_and_summarize(base_url, max_depth=2, max_sub_urls=10):
    visited = set()
    queue = [(base_url, 0)]
    base_dir = 'crawled_content'
    
    task_count = 0
    total_tasks = 1  # Initially, we only have the base_url as the task
    saved_files = []

    while queue:
        current_url, depth = queue.pop(0)
        task_count += 1
        print(f"Working on task {task_count}/{total_tasks}: {current_url}")

        if current_url in visited or depth > max_depth:
            continue
        
        try:
            html_content = get_page_content(current_url)
        except requests.RequestException as e:
            print(f"Failed to fetch {current_url}: {e}")
            continue
        
        text_content = extract_text_content(html_content)
        file_path = save_text_content(base_dir, current_url, text_content)
        saved_files.append(file_path)
        
        visited.add(current_url)
        
        if depth < max_depth:
            sub_urls = find_sub_urls(current_url, html_content, max_sub_urls)
            new_tasks = [(sub_url, depth + 1) for sub_url in sub_urls if sub_url not in visited]
            queue.extend(new_tasks)
            total_tasks += len(new_tasks)
        print(f"Finished task {task_count}/{total_tasks}")

    # Check if only one file was written and if it is empty
    if len(saved_files) == 1:
        with open(saved_files[0], 'r', encoding='utf-8') as file:
            content = file.read().strip()
            if not content:
                print("Error: Only one file was written and it is empty.")
                exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Webpage crawler and content summarization tool.")
    parser.add_argument('url', type=str, help='The base URL to start crawling from.')
    parser.add_argument('--depth', type=int, default=2, help='Maximum depth to crawl. Default is 2.')
    parser.add_argument('--max_sub_urls', type=int, default=10, help='Maximum number of sub-URLs to crawl per page. Default is 10.')

    args = parser.parse_args()
    start_url = ensure_url_scheme(args.url)
    crawl_and_summarize(start_url, args.depth, args.max_sub_urls)
