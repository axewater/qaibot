import discord
import logging
from ..utilities import send_large_message
from ..integrations.search_ebay import search_ebay
import json

async def handle_ebay(interaction: discord.Interaction, query: str, max_results: int = 10):
    await interaction.response.defer()
    progress_message = await interaction.followup.send(f"Searching eBay for: '{query}' with max results '{max_results}'...")

    logging.info(f"handle_ebay: Starting to search eBay for '{query}' with max results '{max_results}'")
    try:
        results = search_ebay(query, max_results)
        await progress_message.edit(content=f"Compiling and formatting results for you ...")

        # Parse the JSON results
        results_list = json.loads(results)
        
        # Construct a table-like string with markdown and emoticons
        table_header = f"**{'Name':<50}{'Category':<20}{'Ship To':<20}{'Price':<10}{'Image URL':<50}{'Item URL'}**\n"
        table_header += "-" * 170 + "\n"
        
        table_rows = ""
        for item in results_list:
            table_rows += f"{item['name']:<50}{item['category']:<20}{item['shipto']:<20}{'$' + item['price']:<10}{item['image_url']:<50}{item['item_url']}\n"
        
        formatted_results = table_header + table_rows

        # Send the formatted results using send_large_message
        await send_large_message(interaction, formatted_results, previewurls='no')
    except Exception as e:
        logging.error(f"handle_ebay: An error occurred - {str(e)}")
        await interaction.followup.send("An error occurred while processing your request.")
