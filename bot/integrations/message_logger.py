import discord
from discord.ext import commands
from ..database import SessionLocal
from ..models import BotStatistics, User, UserSetting, AdminSetting, Log, MessageLog
import datetime
import logging

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
        except Exception as e:
            logging.error(f"Failed to log message: {e}")  # Use logging for errors
        finally:
            db_session.close()

def setup(bot):
    bot.add_cog(MessageLogger(bot))
