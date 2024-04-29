# bot/commands/pricewatch.py

import discord
from ..utilities import send_large_message
from ..integrations.tweakers_pricewatch import search_tweakers_pricewatch

async def handle_pricewatch(interaction: discord.Interaction, component_name: str):
    await interaction.response.defer()

    results = search_tweakers_pricewatch(component_name)

    if results is None:
        await interaction.followup.send(f"No results found for '{component_name}'. (Or failed to fetch data from Tweakers Pricewatch.)")
    elif not results:
        await interaction.followup.send(f"No results found for '{component_name}'.")
    else:
        formatted_results = []
        for result in results:
            name = result["name"]
            price = result["price"]
            link = result["link"]
            formatted_results.append(f"**{name}**: {price} - [LINK!](<{link}>)")

        message = "\n".join(formatted_results)
        await send_large_message(interaction, f"**Search Results for '{component_name}':**\n{message}")
