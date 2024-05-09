import discord
import json
from ..integrations.search_amazon import search_amazon
from ..utilities import send_large_message
import logging

async def handle_amazon(interaction: discord.Interaction, search_query: str):
    """
    Handle Amazon search command for Discord.
    """
    await interaction.response.defer()
    logging.info(f"Starting to scrape IPTorrents for '{search_query}'")

    results_json = search_amazon(search_query)
    results = json.loads(results_json)
    results = results[:10]  # Limit the results to a maximum of 10
    if 'error' in results or not results:
        await interaction.followup.send("handle_amazon: No results found or an error occurred.")
    else:
        message = f"**Amazon Search Results for '{search_query}':**\n"
        for result in results:
            title = result.get('Title', 'No title available')
            price = result.get('Price', 'No price available')
            rating = result.get('Rating', 'No rating')
            num_ratings = result.get('Number of Ratings', 'No ratings')
            delivery_date = result.get('Delivery Date', 'No delivery date')
            message += f"**{title}**\nPrice: {price}\nRating: {rating} ({num_ratings} ratings)\nDelivery Date: {delivery_date}\n\n"
        logging.info(f"handle_amazon: Sending {len(results)} results for '{search_query}' to Discord")
        
        await send_large_message(interaction, f"**Amazon Search Results for '{search_query}':**\n{message}")
