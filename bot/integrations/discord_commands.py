# bot/integrations/discord_commands.py
import discord
import logging
from discord import Option
from ..commands.qai import handle_qai
from ..commands.joinconvo import handle_joinconvo
from ..commands.pricewatch import handle_pricewatch
from ..commands.summarize import handle_summarize
from ..commands.research import handle_research
from ..commands.imback import handle_imback
from ..commands.marktplaats import handle_marktplaats
from ..commands.torrent import handle_torrent
from ..commands.iptorrents import handle_iptorrents
from ..commands.mobygames import handle_mobygames
from ..commands.manage import handle_manage
from ..commands.imdb import handle_imdb
from ..commands.amazon import handle_amazon
from ..integrations.image_generator import generate_image
from ..commands.handle_nmap import handle_nmap

async def setup(bot):
    
    # Define slash commands and connect them to their respective handlers
    @bot.slash_command(name="qqai", description="Ask QAI any question... it knows all!")
    async def qai(interaction: discord.Interaction, question: str):
        logging.info(f"QAI command called with question: {question}")
        print(f"QAI command called with question: {question}")
        await handle_qai(interaction, question)

    @bot.slash_command(name="qjoinconvo", description="Let QAI join the conversation (reads last 15 messages).")
    async def joinconvo(interaction: discord.Interaction):
        logging.info("JoinConvo command called")
        await handle_joinconvo(interaction)

    @bot.slash_command(name="qsummarize", description="QAI will summarize the content of a given URL.")
    async def summarize(interaction: discord.Interaction, url: str, context: str = Option(str, default=None, required=False, description="Optional context to guide the summarization.")):
        logging.info(f"Summarize command called with URL: {url} and context: {context}")
        await handle_summarize(interaction, url, context)

    @bot.slash_command(name="qimback", description="I was away for a while, what happened while I was gone? Summarize the last 200 messages.")
    async def imback(interaction: discord.Interaction):
        logging.info("ImBack command called")
        await handle_imback(interaction)

    @bot.slash_command(name="qresearch", description="Let QAI research a topic on the web for you.")
    async def research(interaction: discord.Interaction, 
                       topic: str = Option(str, description="Enter the topic you want to research."), 
                       depth: str = Option(str, default='normal', description="Specify the depth of research: 'quick', 'normal', or 'deep'.")):
        logging.info(f"Research command called with topic: {topic} and depth: {depth}")
        await handle_research(interaction, topic, depth)

    @bot.slash_command(name="qpricewatch", description="Search for component prices on Tweakers Pricewatch.")
    async def pricewatch(interaction: discord.Interaction, component_name: str):
        logging.info(f"Pricewatch command called with component name: {component_name}")
        await handle_pricewatch(interaction, component_name)

    @bot.slash_command(name="qmarktplaats", description="Search for items on Marktplaats.")
    async def marktplaats(interaction: discord.Interaction, search_query: str):
        logging.info(f"Marktplaats command called with search query: {search_query}")
        await handle_marktplaats(interaction, search_query)

    @bot.slash_command(name="qtorrent", description="Search for torrents on MagnetDL.")
    async def torrent(interaction: discord.Interaction, search_query: str):
        logging.info(f"Torrent command called with search query: {search_query}")
        await handle_torrent(interaction, search_query)

    @bot.slash_command(name="qiptorrents", description="Search for torrents on IPTorrents.")
    async def iptorrents(interaction: discord.Interaction, search_query: str):
        logging.info(f"IPTorrents command called with search query: {search_query}")
        await handle_iptorrents(interaction, search_query)

    @bot.slash_command(name="qmobygames", description="Search for games on MobyGames.")
    async def mobygames(interaction: discord.Interaction, search_query: str):
        logging.info(f"MobyGames command called with search query: {search_query}")
        await handle_mobygames(interaction, search_query)

    @bot.slash_command(name="qmanage", description="Manage your settings.")
    async def settings(interaction: discord.Interaction):
        logging.info("Manage command called")
        await handle_manage(interaction)

    @bot.slash_command(name="qimdb", description="Search for movies and shows on IMDb.")
    async def imdb(interaction: discord.Interaction, search_query: str, type: str = Option(str, default='movie', choices=['movie', 'tv'], description="Specify the type: 'movie' or 'tv'.")):
        logging.info(f"IMDb command called with search query: {search_query}")
        await handle_imdb(interaction, search_query, type)

    @bot.slash_command(name="qamazon", description="Search for products on Amazon.")
    async def amazon(interaction: discord.Interaction, search_query: str):
        logging.info(f"Amazon command called with search query: {search_query}")
        await handle_amazon(interaction, search_query)

    @bot.slash_command(name="qimage", description="Generate an image based on a text prompt.")
    async def image(interaction: discord.Interaction, prompt: str):
        logging.info(f"Image command called with prompt: {prompt}")
        image_path = await generate_image(prompt)
        if image_path:
            await interaction.response.send_message(file=discord.File(image_path))
        else:
            await interaction.response.send_message("Failed to generate image.")

    @bot.slash_command(name="qnmap", description="Perform a port scan on a specified IP address or domain.")
    async def nmap(interaction: discord.Interaction, target: str, port_range: str = Option(str, default=None, required=False, description="Specify the port range (e.g., 1-1000).")):
        await handle_nmap(interaction, target, port_range)
