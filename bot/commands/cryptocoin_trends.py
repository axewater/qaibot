import discord
import logging
from ..integrations.search_coingecko import get_trending_coins
from ..utilities import send_large_message

async def handle_cointrends(interaction: discord.Interaction, max_results: int):
    """
    Handle Cryptocoin trends command for Discord.
    """
    logging.info(f"QAI crypto_trends command called with max_results: {max_results}")
    await interaction.response.defer()
    progress_message = await interaction.followup.send("QAI is fetching the latest cryptocurrency data...")

    result = get_trending_coins(max_results=max_results)
    logging.info(f"Trending coins data: {result}")  # Log the result to inspect the data structure
    formatted_result = format_trending_coins(result)
    await send_large_message(interaction, formatted_result)

def format_trending_coins(data):
    """
    Format the trending coins data into a markdown string.
    """
    coins = data["trending_coins"]
    formatted_coins = []
    for i, coin in enumerate(coins, start=1):
        formatted_coin = f"**{i}. {coin['name']} ({coin['symbol']})**\n"
        formatted_coin += f"- 🪙 **BTC:** {coin['prices']['btc']}\n"
        formatted_coin += f"- 💶 **EUR:** {coin['prices']['eur']}\n"
        formatted_coin += f"- 💵 **USD:** {coin['prices']['usd']}\n"
        formatted_coin += f"- 📈 ![Sparkline]({coin['sparkline']})\n"
        formatted_coin += f"- ℹ️ **Description:** {coin['content']['description']}\n\n"
        formatted_coins.append(formatted_coin)
    
    return "**CoinGecko Trending Coins:**\n\n" + "\n".join(formatted_coins)
