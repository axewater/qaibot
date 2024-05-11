import discord, logging
import json
from ..integrations.openai_imagegen import generate_image
from ..utilities import send_large_message

async def handle_makeimage(interaction: discord.Interaction, prompt: str):
    # Acknowledge the interaction first and defer the response
    await interaction.response.defer()
    logging.info(f"handle_makeimage: called with prompt: {prompt}")

    result = json.loads(generate_image(prompt))  # Parse the JSON string to a Python dictionary
    logging.info(f"handle_makeimage: result: {result}")

    if result['status'] == 'success':
        # Use followup to send the message since we deferred the initial response
        await interaction.followup.send(f"Here's your image: Prompt: {prompt} Image: {result['url']}")
    else:
        # If image generation failed, inform the user using followup as well
        await interaction.followup.send("Failed to generate image.")

