import discord
import logging
import json
from ...integrations.security_sshlogin import load_credentials, is_port_open, test_ssh_login
from ...utilities import send_large_message


async def handle_sshlogin(interaction: discord.Interaction, ip_address: str, port: int):
    await interaction.response.defer()
    progress_message = await interaction.followup.send(f"Starting SSH login test on: {ip_address}:{port}")

    logging.info(f"handle_sshlogin: Starting SSH login test on '{ip_address}' with port '{port}'")

    # Check if port is open
    port_open, error = is_port_open(ip_address, port)
    if not port_open:
        message = f"Port {port} is not open on {ip_address}" if not error else f"Error checking port: {error}"
        await interaction.followup.send(message)
        return

    # Load credentials
    credentials, error = load_credentials('default_credentials.json')
    if error:
        await interaction.followup.send(f"Error loading credentials: {error}")
        return

    results = []
    for username, password in credentials:
        success, error = test_ssh_login(ip_address, port, username, password)
        result = {
            'username': username,
            'password': password,
            'success': success
        }
        if error:
            result['error'] = error
        results.append(result)

    formatted_results = []
    for result in results:
        status = "Success" if result['success'] else "Failed"
        formatted_results.append(f"Username: {result['username']}, Password: {result['password']}, Status: {status}")
        if 'error' in result:
            formatted_results.append(f"Error: {result['error']}")

    message = "\n".join(formatted_results)
    await send_large_message(interaction, message)