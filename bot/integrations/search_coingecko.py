import argparse
import json
import requests
import sys, os
import logging

API_URL = "https://api.coingecko.com/api/v3"

# load the API key by importing it from config.py

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


try:
    from ..config import COINGECKO_API_KEY
except ImportError:
    from config import COINGECKO_API_KEY


API_KEY = COINGECKO_API_KEY

def get_coin_price(coin_id, currencies):
    url = f"{API_URL}/simple/price"
    params = {
        "ids": coin_id,
        "vs_currencies": currencies,
        "include_market_cap": "true",
        "include_24hr_vol": "true",
        "include_24hr_change": "true",
        "include_last_updated_at": "true",
    }
    headers = {
        "accept": "application/json",
        "x-cg-demo-api-key": API_KEY,
    }

    response = requests.get(url, headers=headers, params=params)
    return response.json()


def get_trending_coins(max_results):
    logging.info("Fetching trending coins...")
    url = f"{API_URL}/search/trending"
    headers = {
        "accept": "application/json",
        "x-cg-demo-api-key": API_KEY,
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    # Extract relevant price information for each trending coin
    trending_coins = []
    for coin in data["coins"][:max_results]:
        item = coin["item"]
        coin_id = item["id"]
        coin_prices = get_coin_price(coin_id, "btc,eur,usd")
        trending_coin = {
            "id": coin_id,
            "name": item["name"],
            "symbol": item["symbol"],
            "thumb": item["thumb"],
            "prices": {
                "btc": coin_prices[coin_id]["btc"],
                "eur": coin_prices[coin_id]["eur"],
                "usd": coin_prices[coin_id]["usd"],
            },
            "sparkline": f"https://www.coingecko.com/coins/{item['id']}/sparkline.svg",
            "content": {
                "title": f"What is {item['name']}?",
                "description": item.get("content", {}).get("description", "No description available."),
            },
        }
        trending_coins.append(trending_coin)

    return {"trending_coins": trending_coins}


def main():
    parser = argparse.ArgumentParser(description="CoinGecko API Script")
    parser.add_argument("-c", "--coin", help="Search for a specific coin by name")
    parser.add_argument("-t", "--trending", action="store_true", help="Get trending coins")
    parser.add_argument("-m", "--max-results", type=int, default=15, help="Maximum number of trending coins to retrieve (default: 15)")
    args = parser.parse_args()

    if args.coin:
        coin_id = args.coin.lower()
        currencies = "usd,eur"
        result = get_coin_price(coin_id, currencies)
        print(json.dumps(result, indent=2))
    elif args.trending:
        max_results = args.max_results
        result = get_trending_coins(max_results)
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()


def get_coin_price_api(coin_id, currencies):
    return get_coin_price(coin_id, currencies)


def get_trending_coins_api(max_results):
    return get_trending_coins(max_results)


if __name__ == "__main__":
    main()
