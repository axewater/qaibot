import discord
import logging
import json
from ..utilities import send_large_message
from ..integrations.search_virustotal import query_virustotal, process_data

async def handle_virustotal(interaction: discord.Interaction, query: str, report_type='quick'):
    await interaction.response.defer()
    logging.info(f"handle_virustotal: Starting to scrape VirusTotal for '{query} with report type '{report_type}'")
    try:
        results = query_virustotal(query, 'domain')
        processed_results = process_data(results)
        formatted_results = []
        # Format Domain Information
        if report_type == 'quick' or report_type == 'full':
            domain_info = processed_results['Domain Information']
            # formatted_results.append("**Domain Information**\n" + "\n".join([f"{key}: {value}" for key, value in domain_info.items()]))
        # Format Security Overview
        if report_type == 'quick' or report_type == 'full':
            security_overview = processed_results['Security Overview']
            # formatted_results.append("\n**Security Overview**\n" + "\n".join([f"{key}: {value}" for key, value in security_overview.items()]))
        # Format DNS Records
        if report_type == 'full':
            dns_records = processed_results['DNS Records']
            formatted_results.append("\n**DNS Records**")
            for record in dns_records:
                formatted_results.append(f"Type: {record['Type']}, Value: {record['Value']}")
        # Format Certificate Validity
        if report_type == 'full':
            certificate_validity = processed_results['Certificate Validity']
            formatted_results.append("\n**Certificate Validity**\n" + "\n".join([f"{key}: {value}" for key, value in certificate_validity.items()]))
        message = "\n".join(formatted_results)
        await send_large_message(interaction, message)
    except Exception as e:
        logging.error(f"handle_virustotal: An error occurred - {str(e)}")
        await interaction.followup.send("An error occurred while processing your request.")
