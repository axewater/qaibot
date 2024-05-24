import requests
from bs4 import BeautifulSoup
import logging
import sys
import json

def get_crypto_value(url, coin_name):
    logging.info(f"get_crypto_value: Starting to scrape coingecko.com for {coin_name} value.")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Connection": "keep-alive",
        "Referer": "https://www.google.com",
        "Cache-Control": "no-cache",
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"get_crypto_value: Failed to retrieve data for {coin_name}: {e}")
        return json.dumps({"error": f"Failed to retrieve data for {coin_name}", "details": str(e)})

    logging.info(f"get_crypto_value: Received response with status code: {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')
    value_span = soup.find('span', {'data-converter-target': 'price'})

    if not value_span:
        logging.warning(f"get_crypto_value: {coin_name} value span not found.")
        return json.dumps({"error": f"{coin_name} value span not found"})

    value = value_span.text.strip()
    logging.info(f"get_crypto_value: Extracted {coin_name} value: {value}")

    result = {
        "crypto_coin": coin_name,
        "fiat_currency": "USD",
        "value": value
    }

    return json.dumps(result, indent=4)

if __name__ == "__main__":
    if len(sys.argv) != 1:
        print("Usage: python search_coingecko.py")
        sys.exit(1)

    coins = [
        {"name": "Ethereum", "url": "https://www.coingecko.com/en/coins/ethereum"},
        {"name": "Litecoin", "url": "https://www.coingecko.com/en/coins/litecoin"},
        {"name": "Dogecoin", "url": "https://www.coingecko.com/en/coins/dogecoin"},
        {"name": "Shiba Inu", "url": "https://www.coingecko.com/en/coins/shiba-inu"},
        {"name": "Polkadot", "url": "https://www.coingecko.com/en/coins/polkadot"},
        {"name": "USDC", "url": "https://www.coingecko.com/en/coins/usdc"},
        {"name": "Cardano", "url": "https://www.coingecko.com/en/coins/cardano"},
        {"name": "Monero", "url": "https://www.coingecko.com/en/coins/monero"},
        {"name": "Bitcoin Cash", "url": "https://www.coingecko.com/en/coins/bitcoin-cash"},
        {"name": "XRP", "url": "https://www.coingecko.com/en/coins/xrp"}
    ]

    for coin in coins:
        coin_value_json = get_crypto_value(coin["url"], coin["name"])
        print(coin_value_json)
