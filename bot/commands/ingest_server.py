# bot/commands/ingest_server.py
import discord
import logging
from discord.ext import commands
from ..database import SessionLocal
from ..models import ServerIndexMarker, MessageLog, User

def index_server_messages(interaction: discord.Interaction):
    server = interaction.guild
    readback_old(server)

def readback_old(server):
    db_session = SessionLocal()
    try:
        logging.info(f"readback_handler: Indexing server '{server.name}'")
        
        total_messages = 0
        message_count = 0
        known_users = set()
        
        logging.info(f"readback_handler: Fetching messages for server '{server.name}'")
        for channel in server.channels:
            logging.info(f"readback_handler: Fetching messages from channel '{channel.name}'")
            if isinstance(channel, discord.TextChannel):
                logging.info(f"readback_handler: Fetching messages with limit none")
                for message in channel.history(limit=None):
                    logging.info(f"readback_handler: Checking if message if from the bot itself")
                    if not message.author.bot:
                        if message.author.id not in known_users:
                            user = db_session.query(User).filter(User.user_discord_id == message.author.id).first()
                            if not user:
                                user = User(user_discord_id=message.author.id, username=message.author.name)
                                db_session.add(user)
                                db_session.commit()
                            known_users.add(message.author.id)

                        log_entry = MessageLog(
                            server_id=str(server.id),
                            server_name=server.name,
                            channel_id=str(channel.id),
                            channel_name=channel.name,
                            user_id=message.author.id,
                            message_content=message.content,
                            timestamp=message.created_at
                        )
                        db_session.add(log_entry)
                        total_messages += 1
                        message_count += 1
                        if message_count % 100 == 0:
                            db_session.commit()
                            logging.info(f"readback_handler: Logged {message_count} messages in {server.name}/{channel.name} (Total: {total_messages})")

        db_session.commit()
        logging.info(f"readback_handler: Total messages logged: {total_messages}")
    except Exception as e:
        logging.error(f"readback_handler: Failed to index server {server.name}: {e}")
    finally:
        db_session.close()