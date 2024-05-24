import discord
import logging
from discord.ext import commands
from ..database import SessionLocal
from ..models import ServerIndexMarker, MessageLog, User

class ReadbackHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def index_server_messages(self, interaction: discord.Interaction):
        await interaction.response.defer()
        progress_message = await interaction.followup.send(f"QAI is alles aan het leeg slurpen .. momentje hoor. ")

        server = interaction.guild
        db_session = SessionLocal()
        try:
            # Check if server is already indexed
            logging.info(f"readback_handler: Indexing server '{server.name}'")
            marker = db_session.query(ServerIndexMarker).filter(ServerIndexMarker.server_id == str(server.id)).first()
            if marker and marker.indexed:
                logging.info(f"readback_handler: server '{server.name}' already indexed")
                await interaction.followup.send("Server has already been indexed.")
                return  # Server already indexed, skip

            # Mark server as indexed
            if not marker:
                marker = ServerIndexMarker(server_id=str(server.id), indexed=True)
                db_session.add(marker)
            else:
                marker.indexed = True
            db_session.commit()

            # Initialize message count and total messages
            total_messages = 0
            message_count = 0
            known_users = set()

            # Fetch and log all messages, and ensure all users are in the database
            logging.info(f"readback_handler: Fetching messages for server '{server.name}'")
            for channel in server.channels:
                if isinstance(channel, discord.TextChannel):
                    async for message in channel.history(limit=None):
                        if not message.author.bot:
                            # Check if user exists in the database or in the known set
                            if message.author.id not in known_users:
                                user = db_session.query(User).filter(User.user_discord_id == message.author.id).first()
                                if not user:
                                    user = User(user_discord_id=message.author.id, username=message.author.name)
                                    db_session.add(user)
                                    db_session.commit()  # Commit immediately to ensure user exists for message logging
                                known_users.add(message.author.id)

                            # Log the message
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
                            if message_count % 100 == 0:  # Commit every 100 messages
                                db_session.commit()
                                logging.info(f"readback_handler: Logged {message_count} messages in {server.name}/{channel.name} (Total: {total_messages})")

            # Commit any remaining messages
            db_session.commit()
            logging.info(f"readback_handler: Total messages logged: {total_messages}")

            await interaction.followup.send("readback_handler: Server indexing complete.")
        except Exception as e:
            await interaction.followup.send(f"readback_handler: Failed to index server {server.name}: {e}")
        finally:
            db_session.close()

def setup(bot):
    bot.add_cog(ReadbackHandler(bot))
