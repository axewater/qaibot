# bot/utilities.py
import re  # Import regular expression module
from .integrations.openai_chat import summarize_text
import tiktoken
import logging
import time
import discord

TOKEN_LIMIT = 8000
DISCORD_LIMIT = 2000  # Maximum characters for Discord messages


# Function to determine if a user is member of the Discord server role 'qbotadmins'
def is_admin(user):
    """Check if a user is a member of the Discord server role 'qbotadmins'."""
    return any(role.name == 'qbotadmins' for role in user.roles)

# Function to send large messages, respecting Discord's character limit
async def send_large_message(interaction, message, previewurls='yes'):
    """Send a large message in chunks to respect Discord's character limit without cutting lines in half."""
    if previewurls == 'no':
        # Regex to find URLs in the message
        url_pattern = r'https?://\S+'
        # Replace URLs with bracketed version to prevent previews
        message = re.sub(url_pattern, r'<\g<0>>', message)
    
    if len(message) <= DISCORD_LIMIT:
        await interaction.followup.send(message)
    else:
        # Break the message into chunks, avoiding line cuts
        start = 0
        while start < len(message):
            end = start + DISCORD_LIMIT  # Initial end point

            # If the message is too long, find a newline to break at
            if end < len(message) and '\n' in message[start:end]:
                end = message.rfind('\n', start, end) + 1

            part = message[start:end]
            logging.info(f"send_large_message: Sending message chunk {start // DISCORD_LIMIT + 1}")
            await interaction.followup.send(part)
            
            # Move to the next chunk
            start = end

# Function to summarize content, handling token limits
async def summarize_content(content, context, max_chunks=10):
    """Summarize the content, splitting into chunks if it exceeds the token limit."""
    chunks = chunk_text(content)
    total_chunks = len(chunks)  # Determine the total number of chunks
    summaries = []

    for i, chunk in enumerate(chunks):
        if i >= max_chunks:
            logging.info(f"summarize_content: Limit reached. Processed {max_chunks} chunks out of {total_chunks}.")
            break
        logging.info(f"summarize_content: Processing chunk {i + 1} of {max_chunks}")  # Display current chunk and total
        summary = summarize_text(chunk, context)  # Summarize each chunk
        summaries.append(summary)

    # If more than one summary, combine and summarize again
    if len(summaries) > 1:
        combined_summary = " ".join(summaries)
        logging.info("summarize_content: Summarizing the mother of all summaries")  # When creating a combined summary
        final_summary = summarize_text(combined_summary, context)
        return final_summary
    else:
        return summaries[0]  # If there's only one chunk, return its summary
    
    
# Function to split text into chunks based on the token limit
def chunk_text(content, token_limit=TOKEN_LIMIT):
    """Split text into chunks based on token count."""
    tokenizer = get_tokenizer()
    tokens = tokenizer.encode(content)

    # Print console message if the content is too large
    if len(tokens) > token_limit:
        logging.info(f"chunk_text: Content too large! {len(tokens)} tokens detected. Will split into chunks of {token_limit} tokens.")

    # Split the tokens into chunks
    chunks = []
    for i in range(0, len(tokens), token_limit):
        chunk_tokens = tokens[i:i + token_limit]
        chunk_text = tokenizer.decode(chunk_tokens)  # Convert tokens back to text
        chunks.append(chunk_text)

    return chunks

# Set up a tokenizer for GPT-3.5 or GPT-4
def get_tokenizer():
    """Return a tokenizer based on GPT-3.5 or GPT-4 model."""
    return tiktoken.get_encoding("cl100k_base")
