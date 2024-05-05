# bot/commands/marktplaats.py
import discord, json, os, logging
from ..utilities import send_large_message
from ..integrations.search_marktplaats import scrape_marktplaats_items

async def handle_marktplaats(interaction: discord.Interaction, search_query: str):
    await interaction.response.defer()
    logging.info(f"Starting to scrape Marktplaats for '{search_query}'")
    # Define the path to the blacklist file
    blacklist_path = 'bot/commands/blacklist_sellers.json'

    # Check if the blacklist file exists
    if not os.path.exists(blacklist_path):
        logging.error(f"Blacklist file not found: {os.path.abspath(blacklist_path)}")
        await interaction.followup.send(f"Blacklist file not found: {os.path.abspath(blacklist_path)}")
        return  # Exit the function if the file does not exist

    # Load the blacklist if the file exists
    with open(blacklist_path, 'r') as file:
        blacklist = json.load(file)
        blacklist = [name.lower() for name in blacklist]
        logging.info(f"Loaded {len(blacklist)} entries from the blacklist.")

    results = scrape_marktplaats_items(search_query, blacklist)

    if results is None:
        logging.error("Failed to retrieve or parse items from Marktplaats.")
        await interaction.followup.send(f"No results found for '{search_query}'. (Or failed to fetch data from Marktplaats.)")
    elif not results:
        logging.info(f"No results found for '{search_query}'")
        await interaction.followup.send(f"No results found for '{search_query}'.")
    else:
        embeds = []
        logging.info(f"Formatting {len(results)} results for '{search_query}'")
        for result in results:
            title = result["title"]
            price = result["price"]
            link = result["url"]
            image_url = result["image_url"]

            # Create embed for each item
            embed = discord.Embed(title=title, url=link, description=f"{price}", color=discord.Color.blue())
            if image_url != "No image available":
                embed.set_image(url=image_url)
            embed.set_footer(text="Click the title to view the item on Marktplaats")

            # Collect all embeds
            embeds.append(embed)
        
        # Send all embeds in one message
        logging.info(f"Sending {len(results)} results for '{search_query} to Discord'")
        await interaction.followup.send(embeds=embeds)
