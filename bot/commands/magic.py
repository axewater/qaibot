# bot/commands/magic.py

import discord, logging
from ..utilities import send_large_message
from ..integrations.openai_magic import magic_ai

async def handle_magic(interaction: discord.Interaction, query: str):
    await interaction.response.defer()
    logging.info(f"Magic command called with query: {query}")
    
    processed_text = magic_ai(query)
    if processed_text:
        logging.info("Magic command has generated an answer and is sending it to Discord now.")
        message = f"**Original Question:** {query}\n**Response:**\n{processed_text}"
        await send_large_message(interaction, message)
    else:
        logging.error("Error: No response generated.")
        await interaction.followup.send("Error: No response generated.")
