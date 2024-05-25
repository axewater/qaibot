# bot/client.py
import argparse
import discord
import logging
from discord.ext import commands
from discord import Intents
from .config import DISCORD_TOKEN, QAI_VERSION
from .integrations import discord_commands
from .models import BotStatistics
from .database import init_db, SessionLocal
from .manage_db import main as manage_db_main
from .integrations.message_logger import setup as setup_message_logger
from threading import Thread
from .web_app import app


logging.basicConfig(filename='qaibot.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

parser = argparse.ArgumentParser()
parser.add_argument("--noregister", help="Prevent registration of commands", action="store_true")
parser.add_argument("--purge", help="Purge and recreate the database", action="store_true")
args = parser.parse_args()

intents = Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True

bot = discord.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    logging.info(f'{bot.user.name} version {QAI_VERSION} coming online!')

    # Initialize the database first (if necessary)
    try:
        init_db()
        logging.info("QAIBOT: Database initialized successfully.")
    except Exception as e:
        logging.error(f"QAIBOT: Failed to initialize database: {str(e)}")
        # Exiting or error handling code might go here

    session = SessionLocal()
    try:
        last_stat = session.query(BotStatistics).order_by(BotStatistics.id.desc()).first()
        should_register = not args.noregister

        if should_register:
            await discord_commands.setup(bot)
            setup_message_logger(bot)
            
            await bot.sync_commands()
            
            print("QAIBOT: Registered commands:")
            for command in bot.commands:
                logging.info(f"- {command.name}")

            # Update the database with the new version
            new_stat = BotStatistics(notes=f"Registered with version {QAI_VERSION}", last_registered_version=QAI_VERSION)
            session.add(new_stat)
            session.commit()
            logging.info(f"QAIBOT: Commands registered with version {QAI_VERSION}.")
        else:
            logging.error(f"QAIBOT: Commands already registered with version {QAI_VERSION}. This shouldn't happen.")
        if args.purge:
            manage_db_main()

    except Exception as e:
        logging.error(f"QAIBOT: Error during command registration or version check: {str(e)}")
    finally:
        session.close()

def run_flask():
    app.run(host='127.0.0.1', port=5000)

def run(argv):
    global args
    args = parser.parse_args(argv)
    
    # Start Flask in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.start()
    
    bot.run(DISCORD_TOKEN)
