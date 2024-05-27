import argparse
from newsapi import NewsApiClient

def get_news(api_key, query, source, category, language, country):
    newsapi = NewsApiClient(api_key=api_key)
    
    if query:
        articles = newsapi.get_everything(q=query, language=language)
    elif source:
        articles = newsapi.get_top_headlines(sources=source, category=category, language=language, country=country)
    else:
        articles = newsapi.get_top_headlines(category=category, language=language, country=country)
    
    for article in articles['articles']:
        print(article['title'])
        print(article['url'])
        print("\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Retrieve news using the News API')
    parser.add_argument('--api_key', required=True, help='News API key')
    parser.add_argument('--query', help='Search query')
    parser.add_argument('--source', help='News source')
    parser.add_argument('--category', default='general', help='News category (default: general)')
    parser.add_argument('--language', default='en', help='News language (default: en)')
    parser.add_argument('--country', default='us', help='News country (default: us)')

    args = parser.parse_args()
    
    get_news(args.api_key, args.query, args.source, args.category, args.language, args.country)