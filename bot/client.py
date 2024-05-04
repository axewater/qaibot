# bot/client.py
import discord
import logging
from discord.ext import commands
from discord import Intents
from .config import DISCORD_TOKEN, QAI_VERSION
from .integrations import discord_commands
from .models import init_db, Session, BotStatistics

logging.basicConfig(filename='qaibot.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

intents = Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True

bot = discord.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    logging.info(f'{bot.user.name} version {QAI_VERSION} ')
    print(f'{bot.user.name} version {QAI_VERSION} is ready to go!')
    await discord_commands.setup(bot)
    print("Registering commands. This may take a few seconds.")
    print("If this seems *stuck* connecting, you may be throttled by Discord.")
    await bot.sync_commands()
    
    print("Registered commands:")
    for command in bot.commands:
        logging.info(f"- {command.name}")
        print(f"- {command.name}")

    # Initialize the database
    try:
        init_db()
        session = Session()
        new_stat = BotStatistics(notes=f"{QAI_VERSION}")
        session.add(new_stat)
        session.commit()
        session.close()
        print("Database initialized and bot start time logged.")
    except Exception as e:
        logging.error(f"Failed to initialize database or log start time: {str(e)}")
        print(f"Failed to initialize database or log start time: {str(e)}")

def run():
    bot.run(DISCORD_TOKEN)
