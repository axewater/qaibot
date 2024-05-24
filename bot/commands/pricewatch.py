# bot/commands/pricewatch.py
import discord, logging
from ..utilities import send_large_message
from ..integrations.search_pricewatch import search_tweakers_pricewatch

async def handle_pricewatch(interaction: discord.Interaction, component_name: str):
    await interaction.response.defer()
    progress_message = await interaction.followup.send(f"QAI stuurt drones naar Tweakers voor: {component_name}. ")

    logging.info(f"Starting to scrape Pricewatch for '{component_name}'")
    results = search_tweakers_pricewatch(component_name)

    if results is None:
        logging.error("Failed to retrieve or parse items from Tweakers Pricewatch.")
        await interaction.followup.send(f"No results found for '{component_name}'. (Or failed to fetch data from Tweakers Pricewatch.)")
    elif not results:
        logging.info(f"No results found for '{component_name}'")
        await interaction.followup.send(f"No results found for '{component_name}'.")
    else:
        formatted_results = []
        logging.info(f"Formatting {len(results)} results for '{component_name}'")
        for result in results:
            name = result["name"]
            price = result["price"]
            link = result["link"]
            formatted_results.append(f"**{name}**: {price} - [LINK!](<{link}>)")

        message = "\n".join(formatted_results)
        logging.info(f"Sending {len(results)} results for '{component_name} to Discord'")
        await send_large_message(interaction, f"**Search Results for '{component_name}':**\n{message}")
