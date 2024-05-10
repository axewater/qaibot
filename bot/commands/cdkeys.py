import discord
from ..integrations.search_cdkeys import fetch_game_details

async def handle_search_cdkeys_command(interaction: discord.Interaction, game_name: str):
    await interaction.response.defer()
    results = fetch_game_details(game_name)
    if results:
        await interaction.followup.send(f"CDKeys search results: {results}")
    else:
        await interaction.followup.send("No results found or there was an error.")
