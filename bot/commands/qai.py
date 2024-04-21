# bot/commands/qai.py

import discord
from ..integrations.openai_chat import ask_question
from ..utilities import send_large_message

async def handle_qai(interaction: discord.Interaction, question: str):
    await interaction.response.defer()
    processed_text = ask_question(question)
    if processed_text:
        await send_large_message(interaction, processed_text)
    else:
        await interaction.followup.send("Error: No response received from processing.")
