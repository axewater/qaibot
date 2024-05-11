import discord
import logging
import json  # Import json module to parse JSON string
from ..integrations.search_steam import search_steam
from ..utilities import send_large_message

async def handle_steam(interaction: discord.Interaction, game_name: str):
    await interaction.response.defer()
    logging.info(f"handle_steam: Starting to scrape Steam for '{game_name}'")
    results = search_steam(game_name, output_format='json')
    try:
        results_dict = json.loads(results)  # Parse JSON string to dictionary
        if 'items' in results_dict:  # Check if 'items' key is in the dictionary
            logging.info(f"handle_steam: Found {len(results_dict['items'])} results")
            formatted_results = []
            for result in results_dict['items']:
                game_name = result['name']
                game_id = result['id']
                price_info = result.get('price', {})
                price = f"{price_info.get('currency', 'USD')} {price_info.get('final', 0) / 100:.2f}" if 'final' in price_info else "Price not available"
                image_url = result.get('tiny_image', 'Image not available')
                steam_link = f"https://store.steampowered.com/app/{game_id}"
                formatted_results.append(f"[**{game_name}**]({steam_link}) - Price: {price}\n")
                if image_url != 'Image not available':
                    formatted_results.append(f"![Image]({image_url})\n")

            message = "\n".join(formatted_results)
            await send_large_message(interaction, message)
        else:
            logging.error("handle_steam: No items found in results.")
            await interaction.followup.send("No results found.")
    except json.JSONDecodeError as e:
        logging.error(f"handle_steam: Failed to parse JSON - {str(e)}")
        await interaction.followup.send("Failed to process the search results.")
    except Exception as e:
        logging.error(f"handle_steam: An error occurred - {str(e)}")
        await interaction.followup.send("An error occurred while processing your request.")
