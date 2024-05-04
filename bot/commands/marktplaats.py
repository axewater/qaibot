# bot/commands/marktplaats.py

import discord
from ..utilities import send_large_message
from ..integrations.marktplaats_search import scrape_marktplaats_items

async def handle_marktplaats(interaction: discord.Interaction, search_query: str):
    await interaction.response.defer()

    results = scrape_marktplaats_items(search_query)

    if results is None:
        await interaction.followup.send(f"No results found for '{search_query}'. (Or failed to fetch data from Marktplaats.)")
    elif not results:
        await interaction.followup.send(f"No results found for '{search_query}'.")
    else:
        for result in results:
            title = result["title"]
            price = result["price"]
            link = result["url"]
            image_url = result["image_url"]

            # Create embed for each item
            embed = discord.Embed(title=title, url=link, description=f"{price}", color=discord.Color.blue())
            if image_url != "No image available":
                embed.set_image(url=image_url)
            embed.set_footer(text="Click the title to view the item on Marktplaats")

            # Send the embed
            await interaction.followup.send(embed=embed)