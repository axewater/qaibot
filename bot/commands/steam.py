import discord
from ..integrations.search_steam import search_steam
from ..utilities import send_large_message

async def handle_steam(interaction: discord.Interaction, game_name: str):
    await interaction.response.defer()
    results = search_steam(game_name)
    if results:
        formatted_results = []
        for result in results['items']:
            game_name = result['name']
            price_info = result['price']
            price = f"${price_info['final'] / 100:.2f}" if price_info and 'final' in price_info else "Price not available"
            formatted_results.append(f"**{game_name}** - Price: {price}")

        message = "\n".join(formatted_results)
        await send_large_message(interaction, message)
    else:
        await interaction.followup.send("No results found or there was an error.")
