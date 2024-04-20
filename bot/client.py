# bot/client.py
import discord
from discord import Intents
from .config import DISCORD_TOKEN
from .integrations.openai_chat import process_text_with_gpt

intents = Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True  # Ensure guilds intent is enabled


bot = discord.Bot(command_prefix="!", intents=intents) 

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    await bot.sync_commands() 
    # print the list of commands registered with the bot
    print("Registered commands:")
    for command in bot.commands:
        print(f"- {command.name}")

@bot.slash_command(name="qai", description="Ask QAI any question... it knows all!")
async def qai(interaction: discord.Interaction, command_text: str):
    """Handles the slash command /qai."""
    print(f"Received command: {command_text}")
    processed_text = process_text_with_gpt(command_text)
    if processed_text:
        await interaction.response.send_message(processed_text)
    else:
        await interaction.response.send_message("Error: No response received from processing.")


@bot.slash_command(name="joinconvo", description="Join the conversation by processing the last 5 messages in the channel.")
async def joinconvo(interaction: discord.Interaction):
    """Handles the slash command /joinconvo."""
    print("Received command: /joinconvo")
    channel = interaction.channel
    print(f"Channel: {channel.name}")
    messages = await channel.history(limit=5).flatten()
    print(f"Messages: {messages}")
    context = " ".join([msg.content for msg in messages[::-1]])  # Concatenate the last 5 messages into one string
    processed_text = process_text_with_gpt(context)
    if processed_text:
        await interaction.response.send_message(processed_text)
    else:
        await interaction.response.send_message("Error: No response generated.")


def run():
    bot.run(DISCORD_TOKEN)

