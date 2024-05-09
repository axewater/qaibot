# bot/commands/imdb.py

from ..integrations.search_imdb import search_imdb
from ..utilities import send_large_message
import discord
import logging


async def handle_imdb(interaction: discord.Interaction, query: str, type: str = 'movie'):
    """
    Handle IMDb search command for Discord.
    """
    await interaction.response.defer()
    logging.info(f"Starting to scrape IMDB for '{query}' with type '{type}'")
    results = search_imdb(query, type)
    if not results:
        await interaction.followup.send("IMDB Search: No results found for your query.")
    else:
        formatted_results = []
        for result in results:
            title = result['title']
            year = result['year']
            actors = result['actors']
            link = result['link']
            formatted_results.append(f"**{title} ({year})** - Actors: {actors}, [Link](<{link}>)")
        message = "\n".join(formatted_results)
        await send_large_message(interaction, f"**IMDb Search Results for '{query}':**\n{message}")
