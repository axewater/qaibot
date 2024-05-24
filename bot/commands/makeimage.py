import discord
import logging
import json
import requests
import os
from ..integrations.openai_imagegen import generate_image

# Set up logging
logging.basicConfig(level=logging.INFO)

async def handle_makeimage(interaction: discord.Interaction, prompt: str, size: str='square', quality: str='standard'):
    # Acknowledge the interaction first and defer the response
    await interaction.response.defer()
    progress_message = await interaction.followup.send(f"QAI gaat dit plaatje voor je maken: {prompt}. ")


    logging.info(f"handle_makeimage: called with prompt: {prompt}, size: {size}, quality: {quality}")

    # Generate the image
    result = json.loads(generate_image(prompt, size, quality))
    
    logging.info(f"handle_makeimage: result: {result}")

    if result['status'] == 'success':
        image_url = result['url']
        logging.info(f"Image URL: {image_url}")

        # Create the directory if it does not exist
        save_dir = 'bot/data/images/generated'
        os.makedirs(save_dir, exist_ok=True)
        logging.info(f"Directory '{save_dir}' exists or created.")

        # Download the image
        response = requests.get(image_url)
        if response.status_code == 200:
            logging.info(f"Successfully downloaded image from {image_url}")
            # Extract the filename from the URL
            image_filename = os.path.join(save_dir, image_url.split('?')[0].split('/')[-1])
            with open(image_filename, 'wb') as image_file:
                image_file.write(response.content)
            logging.info(f"Image saved to {image_filename}")

            # Use followup to send the message since we deferred the initial response
            await interaction.followup.send(f"Here's the image you asked for: {prompt}", file=discord.File(image_filename))
        else:
            logging.error(f"Failed to download image. Status code: {response.status_code}")
            await interaction.followup.send("Failed to download the generated image.")
    else:
        logging.error("Image generation failed.")
        await interaction.followup.send("Failed to generate image.")
