async def send_large_message(interaction, message):
    # Discord limits messages to 2000 characters
    max_length = 2000
    if len(message) <= max_length:
        await interaction.followup.send(message)
    else:
        for i in range(0, len(message), max_length):
            await interaction.followup.send(message[i:i+max_length])