import discord
from ..utilities import send_large_message
from ..integrations.search_weather import main as fetch_weather_data

async def handle_weather(interaction: discord.Interaction, location: str):
    await interaction.response.defer()
    try:
        weather_info = fetch_weather_data(location)
        await send_large_message(interaction, weather_info)
    except Exception as e:
        await interaction.followup.send(f"Failed to retrieve weather data: {str(e)}")