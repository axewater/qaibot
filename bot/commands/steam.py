import discord
import logging
import json  # Import json module to parse JSON string
from ..integrations.search_steam import search_steam
from ..utilities import send_large_message

async def handle_steam(interaction: discord.Interaction, game_name: str):
    await interaction.response.defer()
    logging.info(f"handle_steam: Starting to scrape Steam for '{game_name}'")
    results = search_steam(game_name, output_format='json')
    if results:
        results_dict = json.loads(results)  # Parse JSON string to dictionary
        if 'items' in results_dict:  # Check if 'items' key is in the dictionary
            logging.info(f"handle_steam: Results found, formatting now.")
            formatted_results = []
            for result in results_dict['items']:
                game_name = result['name']
                price_info = result['price']
                price = f"${price_info['final'] / 100:.2f}" if price_info and 'final' in price_info else "Price not available"
                formatted_results.append(f"**{game_name}** - Price: {price}")

            message = "\n".join(formatted_results)
            await send_large_message(interaction, message)
        else:
            await interaction.followup.send("No results found or there was an error.")
    else:
        await interaction.followup.send("No results found or there was an error.")
