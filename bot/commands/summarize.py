# bot/commands/summarize.py

import discord
import validators
from ..utilities import send_large_message
from ..integrations.summarize_url import fetch_website_content
from ..utilities import summarize_content

async def handle_summarize(interaction: discord.Interaction, url: str, context: str = None):
    await interaction.response.defer()

    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    if not validators.url(url):
        await interaction.followup.send("The provided string is not a valid URL.")
        return

    content = fetch_website_content(url)

    if content:
        if context is None:
            context = f"Summarize the content at this URL: {url}."

        final_summary = await summarize_content(content, context)

        if final_summary:
            await send_large_message(interaction, f"**SUMMARY OF:** {url}\n{final_summary}")
        else:
            await interaction.followup.send("Error: Could not generate a summary.")
    else:
        await interaction.followup.send(f"Could not fetch or process content from the URL: {url}.")
