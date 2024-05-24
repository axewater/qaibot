import discord
import logging
from ..integrations.search_coingecko import get_crypto_value
from ..utilities import send_large_message

async def handle_coingecko(interaction: discord.Interaction, coin_name: str):
    """
    Handle CoinGecko search command for Discord.
    """
    await interaction.response.defer()
    progress_message = await interaction.followup.send("QAI is fetching the latest cryptocurrency data...")

    # URL for the CoinGecko page of the given coin
    url = f"https://www.coingecko.com/en/coins/{coin_name.replace(' ', '-').lower()}"
    logging.info(f"Fetching data for {coin_name} from {url}")

    result = get_crypto_value(url, coin_name)
    await send_large_message(interaction, f"**CoinGecko Data for {coin_name}:**\n{result}")
