import discord
import logging
from ..utilities import send_large_message
from ..integrations.search_wikipedia import search_wikipedia

async def handle_wikipedia(interaction: discord.Interaction, search_query: str):
    """
    Handle Wikipedia search command for Discord.
    """
    await interaction.response.defer()
    progress_message = await interaction.followup.send("QAI stuurt drones naar Wikipedia voor onderzoek ...")
    logging.info(f"Searching Wikipedia for '{search_query}'")

    # Assuming search_wikipedia returns a JSON string that can be sent directly
    results = search_wikipedia(search_query, num_results=5, language='en')
    
    if results:
        logging.info(f"Sending Wikipedia results to Discord for query '{search_query}'")
        await send_large_message(interaction, results)
    else:
        logging.error(f"No results found for '{search_query}'")
        await interaction.followup.send(f"No results found for '{search_query}'.")
