# bot/client.py
import discord
from discord.ext import commands
from discord import Intents
from .config import DISCORD_TOKEN, OPENAI_API_KEY, GOOGLE_API_KEY
from .integrations.openai_chat import ask_question, join_conversation, summarize_text, process_text_with_gpt

import requests
from bs4 import BeautifulSoup
import validators
from urllib.parse import quote_plus

intents = Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True  # Ensure guilds intent is enabled

bot = discord.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    await bot.sync_commands() 
    print("Registered commands:")
    for command in bot.commands:
        print(f"- {command.name}")

@bot.slash_command(name="qai", description="Ask QAI any question... it knows all!")
async def qai(interaction: discord.Interaction, command_text: str):
    """Handles the slash command /qai."""
    # Defer the interaction response immediately to prevent expiration.
    await interaction.response.defer()
    print(f"Received question: {command_text}")
    
    processed_text = ask_question(command_text)  # Assuming this might take time due to API call.
    if processed_text:
        # Use followup.send() after deferring the initial response.
        await interaction.followup.send(processed_text)
    else:
        await interaction.followup.send("Error: No response received from processing.")


@bot.slash_command(name="joinconvo", description="Let QAI join the conversation (reads last 15 messages).")
async def joinconvo(interaction: discord.Interaction):
    """Handles the slash command /joinconvo."""
    await interaction.response.defer()  # Defer the response to prevent the interaction from expiring

    print("Initiating join conversation command")
    channel = interaction.channel
    messages = await channel.history(limit=15).flatten()
    context = " ".join([msg.content for msg in messages[::-1]])  

    processed_text = join_conversation(context)
    if processed_text:
        await interaction.followup.send(processed_text)  # Use followup.send to send the actual response
    else:
        await interaction.followup.send("Error: No response generated.")


@bot.slash_command(name="summarize", description="Summarize the content of a given URL.")
async def summarize(interaction: discord.Interaction, url: str):
    """Handles the slash command /summarize for a URL."""
    # Ensure the URL starts with http:// or https://
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url  # Prepend 'http://' for compatibility

    # Validate the URL with validators after prepending if necessary
    if not validators.url(url):
        await interaction.response.send_message("The provided string is not a valid URL.")
        return

    await interaction.response.defer()  # Defer the response to prevent the interaction from expiring
    content = fetch_website_content(url)
    if content:
        summary = summarize_text(content)
        # Append the URL to the summary
        response_message = f"**SUMMARY OF:** {url}\n{summary if summary else 'Failed to generate a summary.'}"
        await interaction.followup.send(response_message)
    else:
        await interaction.followup.send(f"Could not fetch or process content from the URL: {url}")



@bot.slash_command(name="research", description="Research a topic and synthesize information from the top 5 search results.")
async def research(interaction: discord.Interaction, topic: str):
    await interaction.response.defer()  # Defer the response immediately to prevent expiration
    
    await interaction.followup.send("Transforming topic into a search query...")
    refined_query = process_text_with_gpt(topic, "Refine this topic into a web search query:")

    await interaction.followup.send(f"Searching the web for: {refined_query}...")
    urls = perform_web_search(refined_query)

    summaries = []
    for url in urls[:5]:  # Limit to the top 5 results
        await interaction.followup.send(f"Summarizing content from {url}...")
        content = fetch_website_content(url)
        if content:
            summary = summarize_text(content)
            summaries.append(summary)
        else:
            await interaction.followup.send(f"Failed to fetch or summarize content from {url}")

    if not summaries:
        await interaction.followup.send("Failed to obtain usable summaries from search results.")
        return

    combined_summary = " ".join(summaries)
    await interaction.followup.send("Synthesizing the information gathered...")
    final_response = process_text_with_gpt(combined_summary, "Provide a comprehensive answer or summary based on the information provided:")

    await interaction.followup.send(f"**Original Question:** {topic}\n**Response:**\n{final_response}")

def perform_web_search(query):
    """Performs a web search using DuckDuckGo and returns the top 5 URLs from the search results."""
    url = "https://lite.duckduckgo.com/lite/"
    # Prepare the payload by encoding the query into the form data
    payload = f'q={quote_plus(query)}&kl=&df='
    headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.7,nl;q=0.3',
      'Accept-Encoding': 'gzip, deflate, br',
      'Referer': 'https://lite.duckduckgo.com/',
      'Content-Type': 'application/x-www-form-urlencoded',
      'Origin': 'https://lite.duckduckgo.com',
      'DNT': '1',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1',
      'Sec-Fetch-Dest': 'document',
      'Sec-Fetch-Mode': 'navigate',
      'Sec-Fetch-Site': 'same-origin',
      'Sec-Fetch-User': '?1',
      'Pragma': 'no-cache',
      'Cache-Control': 'no-cache'
    }

    try:
        print(f"Performing web search for: {query}")
        
        # Send a POST request instead of a GET request
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()  # Will raise an exception for HTTP errors
        print(f"Received text response from search engine: {response.text[:100]}")

        soup = BeautifulSoup(response.text, 'html.parser')
        print("Extracting URLs from search results...")
        # This needs to be tailored to the structure of the search results page
        links = soup.find_all('a', class_='result__url')
        urls = [link['href'] for link in links if validators.url(link['href'])]
        return urls[:5]
    except Exception as e:
        print(f"Failed to perform web search: {e}")
        return []


# def perform_web_search(query):
#     """Performs a web search using the Google Search API and returns the top 5 URLs."""
#     try:
#         from googleapiclient.discovery import build

#         service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
#         res = service.cse().list(
#             q=query, cx="YOUR_SEARCH_ENGINE_ID", num=5  # Replace with your Search Engine ID
#         ).execute()
#         items = res.get("items", [])
#         urls = [item["link"] for item in items]
#         return urls

#     except Exception as e:
#         print(f"Failed to perform web search using Google Search API: {e}")
#         return []


def fetch_website_content(url):
    """Fetches and cleans website content from a URL."""
    try:
        response = requests.get(url)
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

def summarize_text(text):
    """Use the LLM to generate a summary based on the extracted text."""
    print("Summarizing the text with GPT")
    prompt = "Summarize the following text in 1 paragraph. Write the summary in the language of the source text."
    return process_text_with_gpt(text, prompt)



def run():
    bot.run(DISCORD_TOKEN)
