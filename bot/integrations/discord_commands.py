# bot/integrations/discord_commands.py
import discord
import logging
from discord.ext import commands
from discord import Option
from ..commands.qai import handle_qai
from ..commands.joinconvo import handle_joinconvo
from ..commands.pricewatch import handle_pricewatch
from ..commands.summarize import handle_summarize
from ..commands.research import handle_research
from ..commands.imback import handle_imback

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
        print("JoinConvo command called")
        await handle_joinconvo(interaction)

    @bot.slash_command(name="qsummarize", description="QAI will summarize the content of a given URL.")
    async def summarize(interaction: discord.Interaction, url: str, context: str = Option(str, default=None, required=False, description="Optional context to guide the summarization.")):
        logging.info(f"Summarize command called with URL: {url} and context: {context}")
        print(f"Summarize command called with URL: {url} and context: {context}")
        await handle_summarize(interaction, url, context)

    @bot.slash_command(name="qimback", description="I was away for a while, what happened while I was gone? Summarize the last 200 messages.")
    async def imback(interaction: discord.Interaction):
        logging.info("ImBack command called")
        print(f"ImBack command called")
        await handle_imback(interaction)

    @bot.slash_command(name="qresearch", description="Let QAI research a topic on the web for you.")
    async def research(interaction: discord.Interaction, 
                       topic: str = Option(str, description="Enter the topic you want to research."), 
                       depth: str = Option(str, default='normal', description="Specify the depth of research: 'quick', 'normal', or 'deep'.")):
        logging.info(f"Research command called with topic: {topic} and depth: {depth}")
        print(f"Research command called with topic: {topic} and depth: {depth}")
        await handle_research(interaction, topic, depth)

    @bot.slash_command(name="qpricewatch", description="Search for component prices on Tweakers Pricewatch.")
    async def pricewatch(interaction: discord.Interaction, component_name: str):
        logging.info(f"Pricewatch command called with component name: {component_name}")
        print(f"Pricewatch command called with component name: {component_name}")
        await handle_pricewatch(interaction, component_name)
