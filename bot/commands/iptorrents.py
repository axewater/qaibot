# bot/commands/iptorrents.py
import discord, logging
from urllib.parse import urlparse, urlunparse, quote
from ..utilities import send_large_message
from ..integrations.search_iptorrents import search_iptorrents

async def handle_iptorrents(interaction: discord.Interaction, search_query: str):
    """
    Handle IPTorrents search command for Discord.
    """
    
    await interaction.response.defer()
    logging.info(f"Starting to scrape IPTorrents for '{search_query}'")
    results = search_iptorrents(search_query)

    if results is None:
        logging.error("Failed to retrieve or parse items from IPTorrents.")
        await interaction.followup.send("Failed to retrieve or parse items from IPTorrents.")
    elif not results:
        logging.info(f"No results found for '{search_query}'")
        await interaction.followup.send(f"No results found for '{search_query}'.")
    else:
        logging.info(f"Formatting {len(results)} results for '{search_query}'")
        formatted_results = []
        for result in results:
            name = result["Name"]
            size = result["Size"]
            seeders = result["Seeders"]
            leechers = result["Leechers"]
            parsed_url = urlparse(result["Download Link"])
            # Reconstruct URL with the path and query components encoded
            safe_url = urlunparse((
                parsed_url.scheme,
                parsed_url.netloc,
                quote(parsed_url.path),
                parsed_url.params,
                quote(parsed_url.query),
                parsed_url.fragment
            ))
            formatted_results.append(f"**{name}** - Size: {size}, Peers: {seeders}/{leechers}, [LINK!](<{safe_url}>)")

        message = "\n".join(formatted_results)
        logging.info(f"Sending {len(results)} results for '{search_query}' to Discord")
        await send_large_message(interaction, f"**IPTorrents Search Results for '{search_query}':**\n{message}")
