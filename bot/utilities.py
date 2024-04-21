from .integrations.openai_chat import summarize_text
import tiktoken

# Set up a tokenizer for GPT-3.5 or GPT-4
def get_tokenizer():
    """Return a tokenizer based on GPT-3.5 or GPT-4 model."""
    return tiktoken.get_encoding("cl100k_base")

TOKEN_LIMIT = 8000
DISCORD_LIMIT = 2000  # Maximum characters for Discord messages

# Function to split text into chunks based on the token limit
def chunk_text(content, token_limit=TOKEN_LIMIT):
    """Split text into chunks based on token count."""
    tokenizer = get_tokenizer()
    tokens = tokenizer.encode(content)

    # Print console message if the content is too large
    if len(tokens) > token_limit:
        print(f"Content too large! {len(tokens)} tokens detected. Will split into chunks of {token_limit} tokens.")

    # Split the tokens into chunks
    chunks = []
    for i in range(0, len(tokens), token_limit):
        chunk_tokens = tokens[i:i + token_limit]
        chunk_text = tokenizer.decode(chunk_tokens)  # Convert tokens back to text
        chunks.append(chunk_text)

    return chunks


# Function to summarize content, handling token limits
async def summarize_content(content, context):
    """Summarize the content, splitting into chunks if it exceeds the token limit."""
    chunks = chunk_text(content)
    total_chunks = len(chunks)  # Determine the total number of chunks
    summaries = []

    # Processing each chunk with a chunk counter
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i + 1} of {total_chunks}")  # Display current chunk and total
        summary = summarize_text(chunk, context)  # Summarize each chunk
        summaries.append(summary)

    # If more than one summary, combine and summarize again
    if len(summaries) > 1:
        combined_summary = " ".join(summaries)
        print("Summarizing the mother of all summaries")  # When creating a combined summary
        final_summary = summarize_text(combined_summary, context)
        return final_summary
    else:
        return summaries[0]  # If there's only one chunk, return its summary


# Function to send large messages, respecting Discord's character limit
async def send_large_message(interaction, message):
    """Send a large message in chunks to respect Discord's character limit without cutting words in half."""
    if len(message) <= DISCORD_LIMIT:
        await interaction.followup.send(message)
    else:
        # Break the message into chunks, avoiding word cuts
        start = 0
        while start < len(message):
            end = start + DISCORD_LIMIT  # Initial end point

            # If the message is too long, find a space or newline to break at
            if end < len(message):
                while end > start and message[end - 1] not in [' ', '\n']:
                    end -= 1  # Move backward to find a space or newline

                # If no space or newline found, reset to the initial chunk size
                if end == start:
                    end = start + DISCORD_LIMIT

            part = message[start:end]
            print(f"Sending message chunk {start // DISCORD_LIMIT + 1}")
            await interaction.followup.send(part)
            
            # Move to the next chunk
            start = end

