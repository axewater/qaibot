import discord
import logging
from ..integrations.openai_imageanalyze import get_image_description
from ..utilities import send_large_message

async def handle_image_analyze(interaction: discord.Interaction, image_url: str):
    await interaction.response.defer()
    progress_message = await interaction.followup.send(f"Analyzing the image from URL: {image_url}. Please wait...")
    logging.info(f"Image analyze command called with URL: {image_url}. Processing with OpenAI...")

    try:
        description = get_image_description(image_url)
        logging.info("Image description received from OpenAI.")
        message = f"**Image URL:** {image_url}\n**Description:**\n{description}"
        await send_large_message(interaction, message)
    except Exception as e:
        logging.error(f"Error processing image URL: {e}")
        await interaction.followup.send("Error: Unable to process the image URL.")
