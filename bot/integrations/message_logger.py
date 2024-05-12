import discord
from discord.ext import commands
from ..database import SessionLocal
from ..models import User, UserSetting, AdminSetting, Log, MessageLog
import datetime
import logging
import re

class MessageLogger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_count = 0  # Initialize message counter
        logging.basicConfig(level=logging.INFO)  # Configure logging

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.content:
            return  # Ignore bot messages and messages without text content

        db_session = SessionLocal()
        try:
            user = db_session.query(User).filter(User.user_discord_id == message.author.id).first()
            if not user:
                user = User(username=message.author.name, user_discord_id=message.author.id)
                db_session.add(user)
                db_session.commit()

            if not message.guild or not message.channel:
                raise ValueError("Message is missing guild or channel information.")

            log_entry = MessageLog(
                server_id=str(message.guild.id),
                server_name=message.guild.name,
                channel_id=str(message.channel.id),
                channel_name=message.channel.name,
                user_id=user.user_discord_id,  # Convert user_id to string
                message_content=message.content,
                timestamp=message.created_at
            )
            db_session.add(log_entry)
            db_session.commit()
            self.message_count += 1  # Increment message counter
            logging.info(f"Logged Message #{self.message_count}: '{message.content}' in {message.guild.name}/{message.channel.name}")  # Use logging instead of print

            # New URL logging functionality
            urls = re.findall(r'(https?://\S+)', message.content)
            if urls:
                for url in urls:
                    domain_type = self.identify_domain(url)
                    existing_url_log = db_session.query(URLLog).filter(URLLog.url == url, URLLog.user_id == user.user_discord_id).first()
                    if existing_url_log:
                        existing_url_log.mention_count += 1
                        existing_url_log.last_mentioned = datetime.datetime.utcnow()
                    else:
                        new_url_log = URLLog(url=url, domain_type=domain_type, user_id=user.user_discord_id)
                        db_session.add(new_url_log)
                db_session.commit()
            else:
                logging.warning("No URLs found in the message to log.")

        except ValueError as ve:
            logging.warning(str(ve))
        except Exception as e:
            logging.error(f"Failed to log message: {e}")  # Use logging for errors
        finally:
            db_session.close()

    def identify_domain(self, url):
        if "imdb.com" in url:
            return "IMDB"
        elif "steampowered.com" in url:
            return "Steam"
        elif "iptorrents.com" in url or "iptorrents.ru" in url:
            return "IPTorrents"
        elif "torrentleaks.org" in url:
            return "TorrentLeaks"
        elif not url:
            raise ValueError("URL is empty or invalid.")
        return "General"

def setup(bot):
    bot.add_cog(MessageLogger(bot))
