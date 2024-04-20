import requests
from bs4 import BeautifulSoup
from bot.integrations.openai_chat import process_text_with_gpt


def fetch_website_content(url):
    """Fetches and cleans website content from a URL."""
    try:
        response = requests.get(url)
        print(f"Received response from {url}: {response.status_code}")
        response.raise_for_status()  # Will raise an exception for HTTP errors
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove unwanted tag elements
        for script in soup(["script", "style", "header", "footer", "nav", "form"]):
            script.decompose()

        # Get text from the HTML
        text = ' '.join(soup.stripped_strings)
        return text
    except Exception as e:
        print(f"Failed to fetch or clean the website content: {e}")
        return None


def summarize_text(text, context_for_summary):
    """Use the LLM to generate a summary based on the extracted text."""
    print("Summarizing the text with GPT")
    # add the context to the prompt
    system_prompt = context_for_summary
    return process_text_with_gpt(text, system_prompt)

