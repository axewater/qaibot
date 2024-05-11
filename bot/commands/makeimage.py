import discord, logging
import json
from ..integrations.openai_image_generator import generate_image
from ..utilities import send_large_message

async def handle_makeimage(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer()
    logging.info(f"handle_makeimage: called with prompt: {prompt}")
    result = json.loads(generate_image(prompt))  # Parse the JSON string to a Python dictionary
    logging.info(f"handle_makeimage: result: {result}")
    if result['status'] == 'success':
        
        await send_large_message(f"Here's your image: {result['url']}")

    else:
        await interaction.followup.send("Failed to generate image.")
