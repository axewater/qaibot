import discord
from ..integrations.search_steam import search_steam

async def handle_steam(interaction: discord.Interaction, game_name: str):
    await interaction.response.defer()
    results = search_steam(game_name)
    if results:
        await interaction.followup.send(f"Steam search results: {results}")
    else:
        await interaction.followup.send("No results found or there was an error.")
