# bot/commands/summarize.py
import discord, logging
try:
    from ..utilities import send_large_message, summarize_content
    from ..integrations.summarize_url import fetch_website_content
except ImportError:
    # Fallback to absolute imports
    from bot.utilities import send_large_message, summarize_content
    from integrations.summarize_url import fetch_website_content
# suggest install 'validators' if not installed
try:
    import validators
except ImportError:
    print("Module 'validators' is not installed. Please install it using 'pip install validators'")
    raise

async def handle_summarize(interaction: discord.Interaction, url: str, context: str = None):
    await interaction.response.defer()
    logging.info(f"handle_summarize: Summarizing '{url}' with context '{context}'")
    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    if not validators.url(url):
        logging.error(f"handle_summarize: The provided string '{url}' is not a valid URL.")
        await interaction.followup.send("Sorry, but that is not a valid URL.")
        return

    content = fetch_website_content(url) 

    if content:
        if context is None:
            logging.info("handle_summarize: Setting default summarization context prompt.")
            context = f"Summarize the content at this URL: {url}."

        logging.info("handle_summarize: Summarizing content.")
        final_summary = await summarize_content(content, context)

        if final_summary:
            logging.info("handle_summarize: Summary generated. Sending it to Discord now.")
            await send_large_message(interaction, f"**SUMMARY OF:** <{url}>\n{final_summary}")
        else:
            logging.error("handle_summarize: Sorry, no summary was generated.")
            await interaction.followup.send("Error: Could not generate a summary.")
    else:
        logging.error(f"handle_summarize: Could not fetch or process content from the URL: {url}.")
        await interaction.followup.send(f"Could not fetch or process content from the URL: {url}.")
