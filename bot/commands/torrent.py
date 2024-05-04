import discord
from ..utilities import send_large_message
from ..integrations.search_magnetdl import search_torrents

async def handle_torrent(interaction: discord.Interaction, search_query: str):
    await interaction.response.defer()

    results = search_torrents(search_query)

    if results is None:
        await interaction.followup.send(f"No results found for '{search_query}'. (Or failed to fetch data from MagnetDL.)")
    elif not results:
        await interaction.followup.send(f"No results found for '{search_query}'.")
    else:
        formatted_results = []
        for result in results:
            download_name = result['Download Name']
            age = result['Age']
            type = result['Type']
            size = result['Size']
            seeders = result['SE']
            leechers = result['LE']
            magnet_link = result['Magnet Link']
            detail_page_url = result['Detail Page URL']
            # formatted_results.append(
            #     f"**{download_name}** - {type}, {size}, Age: {age}, Seeders: {seeders}, Leechers: {leechers} | [MAGNET!]({magnet_link}) | [More Info](<{detail_page_url}>)"
            # )
            formatted_results.append(
                f"**{download_name}** - {type}, {size}, Age: {age}, Seeders: {seeders}, [Download](<{detail_page_url}>)"
            )
            
        message = "\n".join(formatted_results)
        await send_large_message(interaction, f"**Search Results for '{search_query}':**\n{message}")
