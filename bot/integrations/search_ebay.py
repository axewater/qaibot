import os
import json
import requests
from ebaysdk.finding import Connection

# eBay API credentials
APP_ID = 'Allanvan-qaibot-PRD-65ebc3657-8148e2a8'
DEV_ID = 'c0cede43-06aa-4d67-8964-1a1e3cb09795'
CERT_ID = 'PRD-5ebc36570186-2003-4948-8934-60bb'

def search_ebay(query):
    try:
        api = Connection(appid=APP_ID, config_file=None)
        response = api.execute('findItemsByKeywords', {'keywords': query})

        items = response.reply.searchResult.item[:10]  # Limit to 10 items

        results = []
        for item in items:
            item_info = {
                'name': item.title,
                'price': item.sellingStatus.currentPrice.value,
                'seller_name': item.sellerInfo.sellerUserName,
                'positive_reviews': item.sellerInfo.positiveFeedbackPercent,
                'image_url': item.galleryURL
            }
            results.append(item_info)

        return json.dumps(results, indent=2)

    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def search_ebay_json(query):
    return search_ebay(query)

if __name__ == '__main__':
    search_query = input("Enter the item you want to search for on eBay: ")
    results = search_ebay(search_query)
    if results:
        print(results)