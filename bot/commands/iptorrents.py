import discord
from ..utilities import send_large_message
from ..integrations.search_iptorrents import scrape_iptorrents

async def handle_iptorrents(interaction: discord.Interaction, search_query: str):
    await interaction.response.defer()

    results = scrape_iptorrents(search_query)

    if results is None:
        await interaction.followup.send("Failed to retrieve or parse items from IPTorrents.")
    elif not results:
        await interaction.followup.send(f"No results found for '{search_query}'.")
    else:
        formatted_results = []
        for result in results:
            name = result["Name"]
            size = result["Size"]
            seeders = result["Seeders"]
            leechers = result["Leechers"]
            download_link = result["Download Link"]
            # formatted_results.append(f"**{name}** - Size: {size}, Seeders: {seeders}, Leechers: {leechers}, [DOWNLOAD!](<{download_link}>)")
            formatted_results.append(f"**{name}** - Size: {size}, Peers: {seeders}/{leechers}, [LINK!](<{download_link}>)")

        message = "\n".join(formatted_results)
        await send_large_message(interaction, f"**IPTorrents Search Results for '{search_query}':**\n{message}")
