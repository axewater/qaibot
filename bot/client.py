# bot/client.py
import discord
from discord import Intents
from .config import DISCORD_TOKEN
from .integrations.openai_chat import process_text_with_gpt

intents = Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

    channel = client.get_channel(693239572158480398)
    
    if channel:
        await channel.send("QAI bot initialized and ready to serve your command.")
    else:
        print("Error: Channel not found.")

@client.event
async def on_message(message):
    if message.author == client.user or not message.content.startswith('/qai '):
        return

    command_text = message.content[len('/qai '):].strip()
    processed_text = process_text_with_gpt(command_text)
    if processed_text:
        await message.channel.send(processed_text)
    else:
        print("Error: The processed text was none.")

def run():
    client.run(DISCORD_TOKEN)
