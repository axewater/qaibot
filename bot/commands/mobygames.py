# bot/commands/mobygames.py
import discord, logging
from ..utilities import send_large_message
from ..integrations.search_mobygames import search_mobygames

async def handle_mobygames(interaction: discord.Interaction, search_query: str):
    await interaction.response.defer()
    logging.info(f"Starting to scrape MobyGames for '{search_query}'")
    results = search_mobygames(search_query)

    if results is None:
        logging.error("Failed to retrieve data from MobyGames.")
        await interaction.followup.send("Failed to retrieve data from MobyGames.")
    elif not results.get('games', []):
        logging.info(f"No results found for '{search_query}'")
        await interaction.followup.send(f"No results found for '{search_query}'.")
    else:
        logging.info(f"Formatting {len(results['games'])} results for '{search_query}'")
        games = results['games']
        formatted_results = []
        for game in games:
            title = game.get("title", "No title available")
            year = game.get("year", "Year not available")
            platforms = ", ".join([platform.get("name", "N/A") for platform in game.get("platforms", [])])
            formatted_results.append(f"**{title}** ({year}) - Platforms: {platforms}")

        message = "\n".join(formatted_results)
        logging.info(f"Sending {len(results['games'])} results for '{search_query} to Discord'")
        await send_large_message(interaction, f"**Search Results for '{search_query}':**\n{message}")
