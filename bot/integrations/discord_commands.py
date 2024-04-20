# bot/integrations/discord_commands.py
import discord
from discord.ext import commands
from .discord_handles import (
    handle_qai,
    handle_joinconvo,
    handle_summarize,
    handle_imback,
    handle_research,
)

async def setup(bot):
    @bot.slash_command(name="qai", description="Ask QAI any question... it knows all!")
    async def qai(interaction: discord.Interaction, question: str):
        await handle_qai(interaction, question)

    @bot.slash_command(name="joinconvo", description="Let QAI join the conversation (reads last 15 messages).")
    async def joinconvo(interaction: discord.Interaction):
        await handle_joinconvo(interaction)

    @bot.slash_command(name="summarize", description="QAI will summarize the content of a given URL.")         
    async def summarize(interaction: discord.Interaction, url: str):
        await handle_summarize(interaction, url)

    @bot.slash_command(name="imback", description="I was away for a while, what happened while I was gone? Summarize the last 200 messages.")
    async def imback(interaction: discord.Interaction):
        await handle_imback(interaction)

    @bot.slash_command(name="research", description="Let QAI research a topic on the web for you.")
    async def research(interaction: discord.Interaction, topic: str):
        await handle_research(interaction, topic)
