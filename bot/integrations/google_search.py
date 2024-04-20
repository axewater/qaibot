from ..config import GOOGLE_API_KEY, GOOGLE_CX
from googleapiclient.discovery import build


def perform_web_search(query):
    """Performs a web search using the Google Search API and returns the top 5 URLs."""
    try:
        print(f"Performing web search for: {query}")
        service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        res = service.cse().list(
            q=query, cx=GOOGLE_CX, num=5
        ).execute()
        # print(f"Received search results from Google API: {res}")
        items = res.get("items", [])
        urls = [item["link"] for item in items]
        # print(f"Received URLs from search results: {urls}")
        return urls

    except Exception as e:
        print(f"Failed to perform web search using Google Search API: {e}")
        return []

