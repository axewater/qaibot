# bot/integrations/discord_handles.py
import discord
import validators
from .openai_chat import ask_question, join_conversation, summarize_text, process_text_with_gpt
from ..utilities import send_large_message, chunk_text, summarize_content
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

    # Summarize the context, with chunking if it exceeds the token limit
    final_summary = await summarize_content(
        context,
        "Summarize the last 200 messages in this channel."
    )

    if final_summary:
        await send_large_message(interaction, f"Summary of the last 200 messages:\n{final_summary}")
    else:
        await interaction.followup.send("Error: Could not generate a summary.")


# Function for processing and responding to the research command
async def handle_research(interaction: discord.Interaction, topic: str):
    await interaction.response.defer()

    # Create an initial progress message
    progress_message = await interaction.followup.send("Initializing research...")

    # Refine the topic into an effective web search query using GPT-3.5
    refined_query = process_text_with_gpt(
        topic,
        "This is a sentence typed by a human that we need to research online. Refine this topic into an effective web search query. Retain the language of the question, do not translate it to English.",
        gpt_version=3
    )

    # Update progress message
    await progress_message.edit(content=f"Refined query: {refined_query}...")

    # Perform a web search and get the actual number of results
    urls = perform_web_search(refined_query)

    # Limit processing to the top 10 results but display the correct progress
    total_results = len(urls)  # Determine total count
    all_summaries = []

    # Summarize each website one at a time with accurate progress indication
    for idx, url in enumerate(urls[:10], start=1):
        content = fetch_website_content(url)

        if content:
            context_for_summary = f"Original question: {topic}. Summarize this content in the context of this question."
            summary = await summarize_content(content, context_for_summary)

            if summary:
                all_summaries.append(summary)
                # Update progress in a single message
                await progress_message.edit(content=f"Summarized website {idx}/{total_results}.")
            else:
                await progress_message.edit(content=f"Failed to summarize content from website {idx}/{total_results}.")
        else:
            await progress_message.edit(content=f"Failed to fetch content from website {idx}/{total_results}.")

    if not all_summaries:
        await progress_message.edit(content="Failed to obtain usable summaries from search results.")
        return

    # Combine individual summaries and generate a final comprehensive response using GPT-4
    final_combined_summary = " ".join(all_summaries)
    context_for_final_response = f"Original question: {topic}. {final_combined_summary}"
    final_response = process_text_with_gpt(
        context_for_final_response,
        "Generate a comprehensive response based on this context.",
        gpt_version=4
    )

    await progress_message.edit(content="Research complete, generating response...")

    await send_large_message(interaction, f"**Original Question:** {topic}\n**Response:**\n{final_response}")



# Function for processing and responding to the summarize command
async def handle_summarize(interaction: discord.Interaction, url: str):
    await interaction.response.defer()

    # Ensure the URL has the correct protocol
    if not url.startswith(("http://", "https://")):
        url = "http://" + url

    # Validate the provided URL
    if not validators.url(url):
        await interaction.followup.send("The provided string is not a valid URL.")
        return

    # Fetch content from the URL
    content = fetch_website_content(url)

    if content:
        # Context for summarizing the fetched content
        context = f"Summarize the content at this URL: {url}."
        
        # Summarize the content with token limit handling
        final_summary = await summarize_content(content, context)

        if final_summary:
            await send_large_message(interaction, f"**SUMMARY OF:** {url}\n{final_summary}")
        else:
            await interaction.followup.send("Error: Could not generate a summary.")
    else:
        await interaction.followup.send(f"Could not fetch or process content from the URL: {url}.")


