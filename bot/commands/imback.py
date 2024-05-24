# bot/commands/imback.py
import discord
import logging
import datetime
from ..utilities import send_large_message, chunk_text
from ..integrations.openai_chat import summarize_text, process_text_with_gpt

async def handle_imback(interaction: discord.Interaction):
    await interaction.response.defer()

    # Read the last 100 messages from the current channel
    logging.info("ImBack command called. Reading last 100 messages.")
    progress_message = await interaction.followup.send("Welcome back! One moment while I read through what you missed...")
    channel = interaction.channel
    messages = await channel.history(limit=200).flatten()

    # Create a combined context from all message contents
    logging.info("Creating a combined context from all message contents.")
    await progress_message.edit(content=f"Combining and summarizing all the messages in my brain...")

    # context = "\n".join([msg.content for msg in messages[::-1]])  # Reverse to keep chronological order
    context = "\n".join([f"{msg.author.name} ({msg.created_at}): {msg.content}" for msg in messages[::-1]])  # Reverse to keep chronological order
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Define the context for summarizing the chunks
    summarize_context = f"This is a list of the past 100 Discord messages of the current channel as of {current_datetime}. You need to summarize the conversation to a maximum of 500 tokens. Retain relevant usernames. Timestamps may be simplified to more human readable terms."


    # Summarize the context in chunks, then combine the summaries
    logging.info("Summarizing the context in chunks, then combining the summaries.")
    chunks = chunk_text(context, 8000)  # Split the text into chunks
    summaries = []

    for i, chunk in enumerate(chunks):
        summary = summarize_text(chunk, summarize_context)  # Summarize each chunk
        logging.info(f"Summary {i+1}/{len(chunks)}")
        await progress_message.edit(content=f"Summarizing chunk {i+1}/{len(chunks)}...")
        summaries.append(summary)

    # Combine all the summaries into one text block
    logging.info("Combining all the summaries into one text block.")
    await progress_message.edit(content=f"Combining all the summaries in my brain...")
    combined_summary = " ".join(summaries)

    # Send the combined summary to GPT for the final response
    recap_context = f"I was away for a while, this is a summary of all the chat history. Please give me a short recap, try to limit yourself to 2000 characters."
    final_request = f"{recap_context}\n\n{combined_summary}"
    logging.info("Sending the combined summary to GPT for the final response.")
    recap = process_text_with_gpt(final_request, recap_context, gpt_version=4)

    # Send the recap to Discord
    logging.info("Sending the recap to Discord.")
    await send_large_message(interaction, f"**Recap:** {recap}")
