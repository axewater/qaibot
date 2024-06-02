import discord
import logging
from ..integrations.search_coingecko import get_coin_price
from ..utilities import send_large_message

async def handle_coinvalues(interaction: discord.Interaction, coin_name: str):
    """
    Handle Cryptocoin values command for Discord.
    """
    await interaction.response.defer()
    progress_message = await interaction.followup.send("QAI is fetching the latest cryptocurrency data...")

    # URL for the CoinGecko page of the given coin

    result = get_coin_price(coin_name, currencies="usd,eur")
    
    # Extract Data
    coin_data = result.get(coin_name, {})
    usd_price = coin_data.get('usd')
    eur_price = coin_data.get('eur')
    usd_market_cap = coin_data.get('usd_market_cap')
    eur_market_cap = coin_data.get('eur_market_cap')
    usd_volume_24h = coin_data.get('usd_24h_vol')
    eur_volume_24h = coin_data.get('eur_24h_vol')
    usd_change_24h = coin_data.get('usd_24h_change')
    eur_change_24h = coin_data.get('eur_24h_change')
    last_updated = coin_data.get('last_updated_at')
    
    # Format Data
    formatted_message = f"**CoinGecko Data for {coin_name}:**\n\n"
    formatted_message += "💰 **Price:**\n"
    formatted_message += f"- USD: ${usd_price}\n"
    formatted_message += f"- EUR: €{eur_price}\n\n"
    formatted_message += "📈 **Market Cap:**\n"
    formatted_message += f"- USD: ${usd_market_cap}\n"
    formatted_message += f"- EUR: €{eur_market_cap}\n\n"
    formatted_message += "🔄 **24h Volume:**\n"
    formatted_message += f"- USD: ${usd_volume_24h}\n"
    formatted_message += f"- EUR: €{eur_volume_24h}\n\n"
    formatted_message += "📉 **24h Change:**\n"
    formatted_message += f"- USD: {usd_change_24h}%\n"
    formatted_message += f"- EUR: {eur_change_24h}%\n\n"
    formatted_message += f"_Last updated at: {last_updated}_"
    
    # Send Message
    await send_large_message(interaction, formatted_message)
