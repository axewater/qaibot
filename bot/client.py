# bot/client.py
import discord
from discord import Intents
from .config import DISCORD_TOKEN
from .integrations.openai_chat import process_text_with_gpt

intents = Intents.default()
intents.messages = True
intents.message_content = True  # Ensure message content intent is enabled in your bot's Discord Developer Portal

bot = discord.Bot(command_prefix="!", intents=intents)  # Use discord.Bot for better support of interactions

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    await bot.sync_commands()  # Syncs application commands with Discord, correct method name is sync_commands

@bot.slash_command(name="qai", description="Interact with QAI using a specific command")
async def qai(interaction: discord.Interaction, command_text: str):
    """Handles the slash command /qai."""
    processed_text = process_text_with_gpt(command_text)
    if processed_text:
        await interaction.response.send_message(processed_text)
    else:
        await interaction.response.send_message("Error: No response received from processing.")

def run():
    bot.run(DISCORD_TOKEN)

