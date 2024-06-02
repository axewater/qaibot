import discord
import logging
import json
from bot.integrations.security_portscan import PortScanner, parse_ports
from bot.utilities import send_large_message

async def handle_portscan(interaction: discord.Interaction, ip_address: str, ports: str = 22):
    await interaction.response.defer()
    progress_message = await interaction.followup.send(f"Starting port scan on: {ip_address}")

    logging.info(f"handle_portscan: Starting port scan on '{ip_address}' with ports '{ports}'")
    
    # Initialize PortScanner
    scanner = PortScanner(services_file='bot/integrations/default_ports.json', timeout=1, max_threads=100)
    
    # Parse custom ports if provided
    if ports:
        custom_ports = [(f"Custom-{port}", port, 'tcp') for port in parse_ports(ports)]
        scanner.services = custom_ports
    
    try:
        results = await scanner.scan_ip(ip_address)
        formatted_results = []
        for port, info in results.items():
            formatted_results.append(f"Port {port}/{info['protocol']} ({info['service']}): {info['status']}\n")
        
        message = "\n".join(formatted_results)
        await send_large_message(interaction, message)
    except Exception as e:
        logging.error(f"handle_portscan: An error occurred - {str(e)}")
        await interaction.followup.send("An error occurred while processing your request.")
