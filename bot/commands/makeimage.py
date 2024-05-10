import discord
from ..integrations.openai_image_generator import generate_image

async def handle_makeimage(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer()
    result = generate_image(prompt)
    if result['status'] == 'success':
        await interaction.followup.send(f"Here's your image: {result['url']}")
    else:
        await interaction.followup.send("Failed to generate image.")
