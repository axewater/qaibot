import discord
import logging
from ..utilities import send_large_message
from ..integrations.search_virustotal import query_domain, query_ip, query_url, query_file_hash, process_ip_data, process_domain_data, process_url_data, process_file_hash_data

async def handle_virustotal(interaction: discord.Interaction, query: str, query_type: str, report_type='quick'):
    await interaction.response.defer()
    logging.info(f"handle_virustotal: Starting to scrape VirusTotal for '{query}' with type '{query_type}' and report type '{report_type}'")
    try:
        if query_type == 'domain':
            results = query_domain(query)
            processed_results = process_domain_data(results)
        elif query_type == 'ip':
            results = query_ip(query)
            processed_results = process_ip_data(results)
        elif query_type == 'url':
            results = query_url(query)
            processed_results = process_url_data(results)
        elif query_type == 'hash':
            results = query_file_hash(query)
            processed_results = process_file_hash_data(results)
        else:
            await interaction.followup.send("Invalid query type specified.")
            return

        formatted_results = []
        if report_type == 'quick':
            quick_info = {key: processed_results[key] for key in processed_results if key in ['Domain ID', 'IP Address', 'Report URL', 'md5']}
            formatted_results.append("**Quick Info**\n" + "\n".join([f"**{key}**: {value}" for key, value in quick_info.items()]))
        if report_type == 'full':
            full_info = "\n".join([f"**{key}**: {value}" for key, value in processed_results.items()])
            formatted_results.append("\n**Full Report**\n" + full_info)

        message = "\n".join(formatted_results)
        await send_large_message(interaction, message, previewurls='no')
    except Exception as e:
        logging.error(f"handle_virustotal: An error occurred - {str(e)}")
        await interaction.followup.send("An error occurred while processing your request.")
