# bot/commands/imdb.py

from ..integrations.search_imdb import search_imdb
from ..utilities import send_large_message
import discord

async def handle_imdb(interaction: discord.Interaction, query: str):
    """
    Handle IMDb search command for Discord.
    """
    results = search_imdb(query)
    if not results:
        await interaction.response.send_message("No results found for your query.", ephemeral=True)
    else:
        embed = discord.Embed(title="IMDb Search Results", description=f"Top results for '{query}':", color=0x00ff00)
        for result in results:
            embed.add_field(name=f"{result['title']} ({result['year']})", value=f"[Link]({result['link']})", inline=False)
            embed.add_field(name="Actors", value=result['actors'], inline=False)
        await send_large_message(interaction, embed)
