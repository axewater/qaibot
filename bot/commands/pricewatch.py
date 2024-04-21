# bot/commands/pricewatch.py

import discord
from ..utilities import send_large_message
from ..integrations.tweakers_pricewatch import search_tweakers_pricewatch
from tabulate import tabulate

async def handle_pricewatch(interaction: discord.Interaction, component_name: str):
    await interaction.response.defer()

    results = search_tweakers_pricewatch(component_name)

    if results:
        headers = ["Component", "Price", "Link"]
        table_data = [(r["name"], r["price"], r["link"]) for r in results]
        table = tabulate(table_data, headers=headers, tablefmt="grid")

        await send_large_message(interaction, f"**Search Results for '{component_name}':**\n```\n{table}\n```")
    else:
        await interaction.followup.send(f"No results found for '{component_name}'.")
