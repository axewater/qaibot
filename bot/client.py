# bot/client.py
import discord
from discord import Intents
from .config import DISCORD_TOKEN
from .integrations.openai_chat import ask_question, join_conversation

intents = Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True  # Ensure guilds intent is enabled

bot = discord.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    await bot.sync_commands() 
    print("Registered commands:")
    for command in bot.commands:
        print(f"- {command.name}")

@bot.slash_command(name="qai", description="Ask QAI any question... it knows all!")
async def qai(interaction: discord.Interaction, command_text: str):
    """Handles the slash command /qai."""
    print(f"Received question: {command_text}")
    processed_text = ask_question(command_text)
    if processed_text:
        await interaction.response.send_message(processed_text)
    else:
        await interaction.response.send_message("Error: No response received from processing.")

@bot.slash_command(name="joinconvo", description="Join the conversation by processing the last 5 messages in the channel.")
async def joinconvo(interaction: discord.Interaction):
    """Handles the slash command /joinconvo."""
    await interaction.response.defer()  # Defer the response to prevent the interaction from expiring

    print("Initiating join conversation command")
    channel = interaction.channel
    messages = await channel.history(limit=15).flatten()
    context = " ".join([msg.content for msg in messages[::-1]])  

    processed_text = join_conversation(context)
    if processed_text:
        await interaction.followup.send(processed_text)  # Use followup.send to send the actual response
    else:
        await interaction.followup.send("Error: No response generated.")


def run():
    bot.run(DISCORD_TOKEN)
