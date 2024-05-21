import discord
import logging
from ..utilities import send_large_message
from ..integrations.search_weather import main as fetch_weather_data
from ..integrations.openai_chat import report_weather

async def handle_weather(interaction: discord.Interaction, location: str, report_type: str):
    await interaction.response.defer()
    logging.info(f"Weather command received for location: {location} with report type: {report_type}.")
    try:
        weather_info = fetch_weather_data(location, report_type)
        logging.info(f"Weather info fetched: {weather_info}")
        if weather_info:
            # Convert the weather data into a written form using GPT-4
            written_report = report_weather(weather_info, location, report_type)
            if written_report:
                await send_large_message(interaction, written_report)
            else:
                await interaction.followup.send("Failed to generate weather report.")
        else:
            await interaction.followup.send("Failed to retrieve weather data.")
    except Exception as e:
        logging.error(f"Failed to retrieve weather data: {str(e)}")
        await interaction.followup.send(f"Failed to retrieve weather data: {str(e)}")