import discord
import json
from ..integrations.search_amazon import search_amazon
from ..utilities import send_large_message

async def handle_amazon(interaction: discord.Interaction, query: str):
    """
    Handle Amazon search command for Discord.
    """
    results_json = search_amazon(query)
    results = json.loads(results_json)
    if 'error' in results or not results:
        await interaction.response.send_message("No results found or an error occurred.", ephemeral=True)
    else:
        embed = discord.Embed(title="Amazon Search Results", description=f"Top results for '{query}':", color=0x00ff00)
        for result in results:
            title = result.get('Title', 'No title available')
            price = result.get('Price', 'No price available')
            image_url = result.get('Image', None)
            rating = result.get('Rating', 'No rating')
            num_ratings = result.get('Number of Ratings', 'No ratings')
            delivery_date = result.get('Delivery Date', 'No delivery date')
            embed.add_field(name=title, value=f"Price: {price}\nRating: {rating} ({num_ratings} ratings)\nDelivery Date: {delivery_date}", inline=False)
            if image_url:
                embed.set_thumbnail(url=image_url)
        await send_large_message(interaction, embed)



