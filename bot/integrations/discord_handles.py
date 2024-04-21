# bot/integrations/discord_handles.py
import discord
import validators
from .openai_chat import ask_question, join_conversation, summarize_text, process_text_with_gpt
from ..utilities import send_large_message
from .summarize_url import fetch_website_content
from .google_search import perform_web_search
from .tweakers_pricewatch import search_tweakers_pricewatch
from tabulate import tabulate


# Function for processing and responding to the QAI command
async def handle_qai(interaction: discord.Interaction, question: str):
    await interaction.response.defer()
    processed_text = ask_question(question)
    if processed_text:
        await send_large_message(interaction, processed_text)
    else:
        await interaction.followup.send("Error: No response received from processing.")


# Function for processing and responding to the joinconvo command
async def handle_joinconvo(interaction: discord.Interaction):
    await interaction.response.defer()

    channel = interaction.channel
    messages = await channel.history(limit=15).flatten()
    context = " ".join([msg.content for msg in messages[::-1]])  # Reverse to keep chronological order

    processed_text = join_conversation(context)
    if processed_text:
        await send_large_message(interaction, processed_text)
    else:
        await interaction.followup.send("Error: No response generated.")


# Function for processing and responding to the pricewatch command
async def handle_pricewatch(interaction: discord.Interaction, component_name: str):
    await interaction.response.defer()
    
    results = search_tweakers_pricewatch(component_name)

    if results:
        # Create a tabular output
        headers = ["Component", "Price", "Link"]
        table_data = [(r["name"], r["price"], r["link"]) for r in results]
        table = tabulate(table_data, headers=headers, tablefmt="grid")

        await send_large_message(interaction, f"**Search Results for '{component_name}':**\n```\n{table}\n```")
    else:
        await interaction.followup.send(f"No results found for '{component_name}'.")
        
        
# Function for processing and responding to the imback command
async def handle_imback(interaction: discord.Interaction):
    await interaction.response.defer()

    channel = interaction.channel
    messages = await channel.history(limit=200).flatten()
    context = " ".join([msg.content for msg in messages[::-1]])  # Reverse chronological order

    # Tokenization count threshold
    token_limit = 4000
    words = context.split()

    # If context exceeds the token limit, split into smaller chunks
    if len(words) > token_limit:
        print("Context exceeds token limit. Splitting into chunks...")
        # Split into chunks of 4000 tokens
        chunk_size = token_limit
        chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
        print(f"Split into {len(chunks)} chunks.")

        summaries = []

        # Summarize each chunk
        for chunk in chunks:
            summary = summarize_text(chunk)  # Summarize each chunk
            print(f"Summary of chunk number {chunks.index(chunk) + 1}")
            summaries.append(summary)

        # Combine the summaries and create a final summary
        print("Combining summaries...")
        combined_summary = " ".join(summaries)
        final_summary = summarize_text(combined_summary)
        print("Final summary generated.")

        if final_summary:
            print("Sending final summary of conversation...")
            await send_large_message(interaction, f"Summary of the last 200 messages:\n{final_summary}")
        else:
            await interaction.followup.send("Error: Could not generate a summary.")
    else:
        # If within the token limit, summarize the whole context
        summary = summarize_text(context)

        if summary:
            await send_large_message(interaction, f"Summary of the last 200 messages:\n{summary}")
        else:
            await interaction.followup.send("Error: Could not generate a summary.")

# Function for processing and responding to the research command
async def handle_research(interaction: discord.Interaction, topic: str):
    await interaction.response.defer()

    # Refine the topic into an effective web search query using GPT-3.5
    refined_query = process_text_with_gpt(
        topic,
        "This is a sentence typed by a human that we need to research online. Refine this topic into an effective web search query.",
        gpt_version=3
    )

    await interaction.followup.send(f"Researching the topic: {refined_query}...")

    # Perform a web search and summarize each website individually
    urls = perform_web_search(refined_query)

    all_summaries = []
    for url in urls[:15]:  # Limit to the top 15 results
        obfuscated_url = url.replace("http", "hxxp")
        content = fetch_website_content(url)

        if content:
            # Split and summarize content if it exceeds the token limit
            token_limit = 4000
            words = content.split()

            if len(words) > token_limit:
                # Split into chunks and summarize each separately
                chunk_size = token_limit
                chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
                summaries = []

                for chunk in chunks:
                    summary = summarize_text(
                        chunk,
                        context_for_summary=f"Original question: {topic}. Summarize this content in the context of this question."
                    )
                    summaries.append(summary)
                
                # Combine the summaries of chunks into one summary per content
                combined_summary = " ".join(summaries)
                all_summaries.append(combined_summary)
            else:
                # Summarize content directly if it is within the token limit
                summary = summarize_text(
                    content,
                    context_for_summary=f"Original question: {topic}. Summarize this content in the context of this question."
                )
                all_summaries.append(summary)
        else:
            await interaction.followup.send(f"Failed to fetch or summarize content from {obfuscated_url}")

    if not all_summaries:
        await interaction.followup.send("Failed to obtain usable summaries from search results.")
        return

    # Combine individual summaries and generate a final comprehensive response using GPT-4
    final_combined_summary = " ".join(all_summaries)
    context_for_final_response = f"Original question: {topic}. {final_combined_summary}"
    final_response = process_text_with_gpt(
        context_for_final_response,
        "Generate a comprehensive response based on this context. Answer the question in detail, but limit your output to about 500 tokens.",
        gpt_version=4
    )

    await send_large_message(interaction, f"**Original Question:** {topic}\n**Response:**\n{final_response}")



# Function for processing and responding to the summarize command
async def handle_summarize(interaction: discord.Interaction, url: str):
    await interaction.response.defer()

    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    if not validators.url(url):
        await interaction.followup.send("The provided string is not a valid URL.")
        return

    content = fetch_website_content(url)

    if content:
        token_limit = 4000
        words = content.split()

        if len(words) > token_limit:
            # Split into chunks and summarize each separately
            chunk_size = token_limit
            chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]

            summaries = []
            for chunk in chunks:
                summary = summarize_text(chunk, context_for_summary=f"Summarize this part of the content.")
                summaries.append(summary)

            combined_summary = " ".join(summaries)
            final_summary = summarize_text(
                combined_summary,
                context_for_summary=f"Generate a final summary from the individual summaries.",
                gpt_version=3
            )

            response_message = f"**SUMMARY OF:** {url}\n{final_summary}"
            await send_large_message(interaction, response_message)
        else:
            # Content within token limit, direct summary
            summary = summarize_text(content, context_for_summary=f"Summarize the content at this URL: {url}")
            response_message = f"**SUMMARY OF:** {url}\n{summary if summary else 'Failed to generate a summary.'}"
            await send_large_message(interaction, response_message)
    else:
        await interaction.followup.send(f"Could not fetch or process content from the URL: {url}")

