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
        
        server = interaction.guild
        db_session = SessionLocal()
        try:
            # Check if server is already indexed
            logging.info(f"readback_handler: Indexing server '{server.name}'")
            progress_message = await interaction.followup.send(f"QAI is alles aan het leeg slurpen van server: {server.name}. Momentje hoor... ")
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

            # Collect all unique user IDs
            logging.info(f"readback_handler: Fetching user IDs for server '{server.name}'")
            await progress_message.edit(content=f"FF kijken welke users er in {server.name} zitten. ")

            user_ids = set()
            for channel in server.channels:
                if isinstance(channel, discord.TextChannel):
                    async for message in channel.history(limit=None):
                        if not message.author.bot:
                            user_ids.add((message.author.id, message.author.name))

            # Ensure all users are in the database
            existing_users = {user.user_discord_id for user in db_session.query(User.user_discord_id).filter(User.user_discord_id.in_([uid for uid, _ in user_ids]))}
            new_users = [User(user_discord_id=uid, username=name) for uid, name in user_ids if uid not in existing_users]
            logging.info(f"readback_handler: Adding {len(new_users)} new users to the database for server '{server.name}'")
            await progress_message.edit(content=f"Okay, {len(new_users)} users toevoegen aan de database. Momentje hoor. ")

            db_session.bulk_save_objects(new_users)
            db_session.commit()

            # Fetch and log all messages
            logging.info(f"readback_handler: Fetching messages for server '{server.name}'")
            message_count = 0
            for channel in server.channels:
                if isinstance(channel, discord.TextChannel):
                    async for message in channel.history(limit=None):
                        if not message.author.bot:
                            log_entry = MessageLog(
                                server_id=str(server.id),
                                server_name=server.name,
                                channel_id=str(channel.id),
                                channel_name=channel.name,
                                user_id=message.author.id,
                                message_content=message.content,
                                timestamp=message.created_at
                            )
                            message_count += 1
                            db_session.add(log_entry)
                            if message_count % 100 == 0:  # Commit every 100 messages
                                db_session.commit()
                                logging.info(f"readback_handler: Logged 100 messages in {server.name}/{channel.name}")
                                await progress_message.edit(content=f"{message_count} berichten in {server.name}/{channel.name} opgezogen. ")

            db_session.commit()
            await interaction.followup.send("readback_handler: Okay, klaar met zuigen. Alle berichten van server: " + server.name + " staan nu in de database.")
        except Exception as e:
            await interaction.followup.send(f"readback_handler: Kak iets is niet gelukt met het zuigen van {server.name}: {e}")
        finally:
            db_session.close()


def setup(bot):
    bot.add_cog(ReadbackHandler(bot))