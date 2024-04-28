# bot/commands/pricewatch.py

import discord
from ..utilities import send_large_message
from ..integrations.tweakers_pricewatch import search_tweakers_pricewatch

async def handle_pricewatch(interaction: discord.Interaction, component_name: str):
    await interaction.response.defer()

    results = search_tweakers_pricewatch(component_name)

    if results:
        # Create a formatted list of results, one item per line
        formatted_results = []
        for result in results:
            name = result["name"]
            price = result["price"]
            link = result["link"]
            formatted_results.append(f"**{name}**: {price} - <{link}>")  # Wrap the link in < >

        # Join the formatted results into a single message
        message = "\n".join(formatted_results)

        await send_large_message(interaction, f"**Search Results for '{component_name}':**\n{message}")
    else:
        await interaction.followup.send(f"No results found for '{component_name}'.")
