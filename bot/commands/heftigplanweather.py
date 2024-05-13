# bot/commands/weather.py
# This file calls weather.py in 3 manners (now, tomorrow, week)
# These results are sent to OpenAI ChatGPT, with a system prompt in front of it :
# 'Dit is data van het weerbericht. Lees het voor alsof het voor een radio uitzending is. Beperkt de text tot een maximum van 300 karakters, of 500 karakters voor een 'week weer overzicht'

import discord, logging
from ..integrations.openai_chat import report_weather
from ..utilities import send_large_message

async def handle_weather(interaction: discord.Interaction, question: str):
    await interaction.response.defer()
    logging.info(f"Qai was asked the weather for location : {question}.")
    weather_report = processed_text = report_weather(question)
    
    if weather_report:
        logging.info("Qai heeft het weerbericht ontvangen en is het verstuurd naar Discord.")
        
        message = f"**Locatie:** {question}\n**Response:**\n{weather_report}"
        await send_large_message(interaction, message)
                
    else:
        logging.error("Error: No response received from processing at OpenAI.")
        await interaction.followup.send("Error: No response received from processing.")


        