import discord, logging
import json
from ..integrations.openai_imagegen import generate_image

# async def handle_makeimage(interaction: discord.Interaction, prompt: str, size: str, quality: str):
#     # Acknowledge the interaction first and defer the response
#     await interaction.response.defer()
#     logging.info(f"handle_makeimage: called with prompt: {prompt}, size: {size}, quality: {quality}")

#     result = json.loads(generate_image(prompt))  # Parse the JSON string to a Python dictionary
#     logging.info(f"handle_makeimage: result: {result}")

#     if result['status'] == 'success':
#         # Use followup to send the message since we deferred the initial response
#         await interaction.followup.send(f"Here's the image I made: [{prompt}]({result['url']})")
#     else:
#         # If image generation failed, inform the user using followup as well
#         await interaction.followup.send("Failed to generate image.")


async def handle_makeimage(interaction: discord.Interaction, prompt: str, size: str, quality: str):
    # Acknowledge the interaction first and defer the response
    await interaction.response.defer()
    logging.info(f"handle_makeimage: called with prompt: {prompt}, size: {size}, quality: {quality}")

    result = json.loads(generate_image(prompt, size, quality))  # Parse the JSON string to a Python dictionary
    logging.info(f"handle_makeimage: result: {result}")

    if result['status'] == 'success':
        # Use followup to send the message since we deferred the initial response
        await interaction.followup.send(f"Here's the image I made: [{prompt}]({result['url']})")
    else:
        # If image generation failed, inform the user using followup as well
        await interaction.followup.send("Failed to generate image.")
