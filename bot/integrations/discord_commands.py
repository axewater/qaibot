# bot/integrations/discord_commands.py
import discord
import logging
from discord import Option

from ..commands.qai import handle_qai
from ..commands.joinconvo import handle_joinconvo
from ..commands.imback import handle_imback
from ..commands.summarize import handle_summarize
from ..commands.research import handle_research
from ..commands.manage import handle_manage
from ..commands.readback_handler import ReadbackHandler, setup as setup_readback_handler
from ..commands.makeimage import handle_makeimage
from ..commands.admin_settings import handle_admin_settings
from ..commands.marktplaats import handle_marktplaats
from ..commands.pricewatch import handle_pricewatch
from ..commands.torrent import handle_torrent
from ..commands.iptorrents import handle_iptorrents
from ..commands.virustotal import handle_virustotal
from ..commands.imdb import handle_imdb
from ..commands.steam import handle_steam
from ..commands.cdkeys import handle_cdkeys
from ..commands.amazon import handle_amazon

async def setup(bot):
    
    # # Define slash commands and connect them to their respective handlers
    # @bot.slash_command(name="qqqai", description="Ask QAI any question... it knows all!")
    # async def qai(interaction: discord.Interaction, question: str):
    #     logging.info(f"QAI command called with question: {question}")
    #     await handle_qai(interaction, question)
            
            
    # @bot.slash_command(name="qqmakeimage", description="Generate an image based on your text prompt.")
    # async def image(interaction: discord.Interaction, prompt: str):
    #     logging.info(f"Image command called with prompt: {prompt}")
    #     await handle_makeimage(interaction, prompt)

    # @bot.slash_command(name="qqjoinconvo", description="Let QAI join the conversation (reads last 15 messages).")
    # async def joinconvo(interaction: discord.Interaction):
    #     logging.info("JoinConvo command called")
    #     await handle_joinconvo(interaction)
    
    # @bot.slash_command(name="qqimback", description="I was away for a while, what happened while I was gone? Summarize the last 200 messages.")
    # async def imback(interaction: discord.Interaction):
    #     logging.info("ImBack command called")
    #     await handle_imback(interaction)

    # @bot.slash_command(name="qqsummarize", description="QAI will summarize the content of a given URL.")
    # async def summarize(interaction: discord.Interaction, url: str, context: str = Option(str, default=None, required=False, description="Optional context to guide the summarization.")):
    #     logging.info(f"Summarize command called with URL: {url} and context: {context}")
    #     await handle_summarize(interaction, url, context)

    # @bot.slash_command(name="qqresearch", description="Let QAI research a topic on the web for you.")
    # async def research(interaction: discord.Interaction, 
    #                    topic: str = Option(str, description="Enter the topic you want to research."), 
    #                    depth: str = Option(str, default='normal', description="Specify the depth of research: 'quick', 'normal', or 'deep'.")):
    #     logging.info(f"Research command called with topic: {topic} and depth: {depth}")
    #     await handle_research(interaction, topic, depth)

    # @bot.slash_command(name="qqpricewatch", description="Search for component prices on Tweakers Pricewatch.")
    # async def pricewatch(interaction: discord.Interaction, component_name: str):
    #     logging.info(f"Pricewatch command called with component name: {component_name}")
    #     await handle_pricewatch(interaction, component_name)

    # @bot.slash_command(name="qqmarktplaats", description="Search for items on Marktplaats.")
    # async def marktplaats(interaction: discord.Interaction, search_query: str):
    #     logging.info(f"Marktplaats command called with search query: {search_query}")
    #     await handle_marktplaats(interaction, search_query)

    # @bot.slash_command(name="qqtorrent", description="Search for torrents on MagnetDL.")
    # async def torrent(interaction: discord.Interaction, search_query: str):
    #     logging.info(f"Torrent command called with search query: {search_query}")
    #     await handle_torrent(interaction, search_query)

    # @bot.slash_command(name="qqiptorrents", description="Search for torrents on IPTorrents.")
    # async def iptorrents(interaction: discord.Interaction, search_query: str):
    #     logging.info(f"IPTorrents command called with search query: {search_query}")
    #     await handle_iptorrents(interaction, search_query)


    # @bot.slash_command(name="qqimdb", description="Search for movies and shows on IMDb.")
    # async def imdb(interaction: discord.Interaction, search_query: str, type: str = Option(str, default='movie', choices=['movie', 'tv'], description="Specify the type: 'movie' or 'tv'.")):
    #     logging.info(f"IMDb command called with search query: {search_query}")
    #     await handle_imdb(interaction, search_query, type)

    @bot.slash_command(name="qqamazon", description="Search for products on Amazon.")
    async def amazon(interaction: discord.Interaction, search_query: str):
        logging.info(f"Amazon command called with search query: {search_query}")
        await handle_amazon(interaction, search_query)

    # @bot.slash_command(name="qqsteam", description="Search for games on Steam.")
    # async def steam_search(interaction: discord.Interaction, game_name: str):
    #     await handle_steam(interaction, game_name)

    # @bot.slash_command(name="qqcdkeys", description="Search for game deals on CDKeys.")
    # async def cdkeys_search(interaction: discord.Interaction, game_name: str):
    #     await handle_cdkeys(interaction, game_name)
        
    # @bot.slash_command(name="qqreadback", description="Index all messages from all channels in this server.")
    # async def readback(interaction: discord.Interaction):
    #     handler = ReadbackHandler(bot)
    #     await handler.index_server_messages(interaction)
    #     await interaction.response.send_message("Server indexing complete.")

    # @bot.slash_command(name="qqmanage", description="Manage your settings.")
    # async def settings(interaction: discord.Interaction):
    #     logging.info("Manage command called")
    #     await handle_manage(interaction)

    # @bot.slash_command(name="qqadminsettings", description="Manage administrator settings.")
    # async def admin_settings(interaction: discord.Interaction):
    #     logging.info("Admin Settings command called")
    #     await handle_admin_settings(interaction)

    
    @bot.slash_command(name="qqvirustotal", description="Query VirusTotal for URLs, domains, IPs, and hashes.")
    async def virustotal(interaction: discord.Interaction, query: str, report_type: str = Option(str, default='quick', choices=['quick', 'full'], description="Choose report type: 'quick' or 'full'.")):
        logging.info(f"VirusTotal command called with query: {query}")
        await handle_virustotal(interaction, query, report_type)

    # Register additional handlers
    setup_readback_handler(bot)
