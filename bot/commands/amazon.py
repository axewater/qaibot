import discord
import json
from urllib.parse import urlparse, urlunparse, quote
from ..integrations.search_amazon import search_amazon
from ..utilities import send_large_message
import logging

async def handle_amazon(interaction: discord.Interaction, search_query: str):
    """
    Handle Amazon search command for Discord.
    """
    await interaction.response.defer()
    logging.info(f"Starting to scrape Amazon for '{search_query}'")

    results_json = search_amazon(search_query)
    results = json.loads(results_json)
    if 'error' in results:
        await interaction.followup.send(f"Amazon Search Error: {results['error']}")
        return
    results = results[:10]  # Limit the results to a maximum of 10
    if not results:
        await interaction.followup.send("handle_amazon: No results found.")
    else:
        logging.info(f"Formatting {len(results)} results for '{search_query}'")
        formatted_results = []
        for result in results:
            title = result.get('Title', 'No title available')
            price = result.get('Price', 'No price available')
            rating = result.get('Rating', 'No rating')
            num_ratings = result.get('Number of Ratings', 'No ratings')
            delivery_date = result.get('Delivery Date', 'No delivery date')
            parsed_url = urlparse(result.get('Link', '#'))
            # Reconstruct URL with the path and query components encoded
            safe_url = urlunparse((
                parsed_url.scheme,
                parsed_url.netloc,
                quote(parsed_url.path),
                parsed_url.params,
                quote(parsed_url.query),
                parsed_url.fragment
            ))
            formatted_results.append(f"**[{title}]({safe_url})**\nPrice: {price}\nRating: {rating} ({num_ratings} ratings)\nDelivery Date: {delivery_date}\n\n")

        message = "\n".join(formatted_results)
        logging.info(f"Sending {len(results)} results for '{search_query}' to Discord")
        await send_large_message(interaction, f"**Amazon Search Results for '{search_query}':**\n{message}")
