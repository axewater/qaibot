from discord.ui import Button, View
import discord
import logging
from ..utilities import is_admin
from .readback_handler import ReadbackHandler

async def handle_admin_settings(interaction: discord.Interaction):
    # Check if the user is an admin
    if is_admin(interaction.user):
        # Create a button for the admin to interact with
        button = Button(label="Test Admin Button", style=discord.ButtonStyle.primary)

        async def on_button_click(interaction: discord.Interaction):
            # Respond to the admin when they click the button
            await interaction.response.send_message("Yesss, you are a bot administrator", ephemeral=True)

        button.callback = on_button_click
        view = View()
        view.add_item(button)
        # Add button for Readback functionality
        readback_button = Button(label="Index Server Messages", style=discord.ButtonStyle.danger)

        async def on_readback_button_click(interaction: discord.Interaction):
            handler = ReadbackHandler(interaction.client)
            await handler.index_server_messages(interaction)

        readback_button.callback = on_readback_button_click
        view.add_item(readback_button)

        await interaction.response.send_message("Click the button to test admin settings:", view=view, ephemeral=True)
    else:
        await interaction.response.send_message("You are not authorized to use this command.", ephemeral=True)