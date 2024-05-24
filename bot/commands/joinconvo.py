# bot/commands/joinconvo.py

import discord, logging
from ..utilities import send_large_message
from ..integrations.openai_chat import join_conversation

async def handle_joinconvo(interaction: discord.Interaction):
    await interaction.response.defer()

    channel = interaction.channel
    progress_message = await interaction.followup.send("QAI wanders into the channel and reads the last few messages ...")

    logging.info("JoinConvo command called. Reading last 15 messages.")
    messages = await channel.history(limit=15).flatten()
    # context = " ".join([msg.content for msg in messages[::-1]])  # Reverse to keep chronological order
    context = "\n".join([f"{msg.author.name} ({msg.created_at}): {msg.content}" for msg in messages[::-1]])  # Reverse to keep chronological order

    processed_text = join_conversation(context)
    if processed_text:
        logging.info("JoinConvo command has generated an answer and is sending it to Discord now.")
        await send_large_message(interaction, processed_text)
    else:
        logging.error("Error: No response generated.")
        await interaction.followup.send("Error: No response generated.")
