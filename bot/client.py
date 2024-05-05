# bot/client.py
import discord
import logging
from discord.ext import commands
from discord import Intents
from .config import DISCORD_TOKEN, QAI_VERSION
from .integrations import discord_commands
from .models import BotStatistics
from .database import init_db, SessionLocal
logging.basicConfig(filename='qaibot.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

intents = Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True

bot = discord.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    logging.info(f'{bot.user.name} version {QAI_VERSION} coming online!')
    
    await discord_commands.setup(bot)
    print("QAIBOT: Registering commands. This may take a few seconds.")
    print("QAIBOT: If this seems *stuck* connecting, you may be RATE LIMITED by Discord.")
    await bot.sync_commands()
    
    print("QAIBOT: Registered commands:")
    for command in bot.commands:
        logging.info(f"- {command.name}")

    # Initialize the database
    try:
        init_db()
        session = SessionLocal()
        new_stat = BotStatistics(notes=f"{QAI_VERSION}")
        session.add(new_stat)
        session.commit()
        session.close()
        logging.info(f"QAIBOT: Database initialized. QaiBot v{QAI_VERSION} start time logged.")
    except Exception as e:
        logging.error(f"QAIBOT: Failed to initialize database or log start time: {str(e)}")
        

def run():
    bot.run(DISCORD_TOKEN)
