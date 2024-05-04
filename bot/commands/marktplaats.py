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
        formatted_results = []
        for result in results:
            title = result["title"]
            price = result["price"]
            formatted_results.append(f"**{title}**: {price}")

        message = "\n".join(formatted_results)
        await send_large_message(interaction, f"**Search Results for '{search_query}':**\n{message}")
