# bot\integrations\discord_commands.py
import discord
from discord.ext import commands
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
        await handle_qai(interaction, question)

    @bot.slash_command(name="qjoinconvo", description="Let QAI join the conversation (reads last 15 messages).")
    async def joinconvo(interaction: discord.Interaction):
        await handle_joinconvo(interaction)

    @bot.slash_command(name="qsummarize", description="QAI will summarize the content of a given URL.")
    async def summarize(interaction: discord.Interaction, url: str):
        await handle_summarize(interaction, url)

    @bot.slash_command(name="qimback", description="I was away for a while, what happened while I was gone? Summarize the last 200 messages.")
    async def imback(interaction: discord.Interaction):
        await handle_imback(interaction)

    @bot.slash_command(name="qresearch", description="Let QAI research a topic on the web for you.")
    async def research(interaction: discord.Interaction, topic: str):
        await handle_research(interaction, topic)

    @bot.slash_command(name="qpricewatch", description="Search for component prices on Tweakers Pricewatch.")
    async def pricewatch(interaction: discord.Interaction, component_name: str):
        await handle_pricewatch(interaction, component_name)
