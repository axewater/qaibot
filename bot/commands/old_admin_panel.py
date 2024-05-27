from discord.ui import Modal, InputText, Button, View
import discord
import logging
from ..utilities import is_admin
from ..integrations.security_portscan import PortScanner, parse_ports
from .ingest_server import ReadbackHandler

class PortScanModal(Modal):
    def __init__(self):
        super().__init__(title="Port Scanner")

        self.ip_or_domain = InputText(label="IP Address or Domain", style=discord.TextStyle.short, placeholder="Enter IP or domain here", required=True)
        self.add_item(self.ip_or_domain)

        self.port_range = InputText(label="Port Range (optional)", style=discord.TextStyle.short, placeholder="Enter port range (e.g., 80,443 or 1-1024)", required=False)
        self.add_item(self.port_range)

    async def on_submit(self, interaction: discord.Interaction):
        ip_or_domain = self.ip_or_domain.value
        port_range = self.port_range.value
        result = perform_port_scan(ip_or_domain, port_range, verbose=False)
        await interaction.response.send_message(f"Scan results for {ip_or_domain}:\n{result}", ephemeral=True)



async def handle_admin_panel(interaction: discord.Interaction):
    if is_admin(interaction.user):
        view = View()

        # Existing button for other admin functionalities
        readback_button = Button(label="Index Server Messages", style=discord.ButtonStyle.danger)
        async def on_readback_button_click(interaction: discord.Interaction):
            handler = ReadbackHandler(interaction.client)
            await handler.index_server_messages(interaction)
        readback_button.callback = on_readback_button_click
        view.add_item(readback_button)

        # New button for port scanning
        scan_button = Button(label="Scan Ports", style=discord.ButtonStyle.success)
        async def on_scan_button_click(interaction: discord.Interaction):
            modal = PortScanModal()
            await interaction.response.send_modal(modal)
        scan_button.callback = on_scan_button_click
        view.add_item(scan_button)

        await interaction.response.send_message("Admin Panel:", view=view, ephemeral=True)
    else:
        await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)
