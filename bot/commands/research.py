# bot/commands/research.py
import discord
import os
from ..utilities import send_large_message, summarize_content

from ..integrations.openai_chat import process_text_with_gpt
from ..integrations.google_search import perform_web_search
from ..integrations.summarize_url import fetch_website_content
import json

# Function to load the blacklist and handle errors
def load_blacklist(blacklist_filename):
    """Loads the blacklist from a JSON file, with error handling."""
    # Get the current script directory
    script_directory = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the full path to the blacklist file
    blacklist_file_path = os.path.join(script_directory, blacklist_filename)
    
    if not os.path.exists(blacklist_file_path):
        print(f"Blacklist file '{blacklist_file_path}' does not exist.")
        return []  # Return an empty list if the file doesn't exist

    if not os.path.isfile(blacklist_file_path):
        print(f"'{blacklist_file_path}' is not a valid file.")
        return []  # Return an empty list if it's not a valid file

    try:
        with open(blacklist_file_path, 'r') as f:
            blacklist = json.load(f)
            if not isinstance(blacklist, list):
                print("Blacklist file content is not a list.")
                return []  # Ensure the content is a list
            print(f"Loaded {len(blacklist)} URLs from the blacklist.")
            return blacklist
    except json.JSONDecodeError:
        print(f"Blacklist file '{blacklist_file_path}' contains invalid JSON.")
        return []  # Return empty if there's a JSON error
    except Exception as e:
        print(f"An error occurred while loading the blacklist: {e}")
        return []  # General exception handling


# Function for processing and responding to the research command
async def handle_research(interaction: discord.Interaction, topic: str):
    await interaction.response.defer()

    progress_message = await interaction.followup.send("Initializing research...")

    # Load the blacklist with additional checks and error handling
    blacklist_filename = 'blacklist_urls.json'  # Only need the filename
    blacklist = load_blacklist(blacklist_filename)

    # Refine the topic into an effective web search query using GPT-3.5
    refined_query = process_text_with_gpt(
        topic,
        "This is a sentence typed by a human that we need to research online. Refine this topic into an effective web search query without translating to another language. Keep English in English, Dutch in Dutch. etc.",
        gpt_version=3
    )

    await progress_message.edit(content=f"Researching the topic: {refined_query}...")

    # Perform a web search and get the actual number of results
    urls = perform_web_search(refined_query)

    # Filter out blacklisted URLs
    urls = [url for url in urls if url not in blacklist]

    # Limit processing to the top 10 results, updating progress
    total_results = len(urls)
    all_summaries = []

    # Summarize each website one at a time
    for idx, url in enumerate(urls[:10], start=1):
        content = fetch_website_content(url)

        if content:
            context_for_summary = f"Original question: {topic}. Summarize this content in the context of this question."
            summary = await summarize_content(content, context_for_summary)

            if summary:
                all_summaries.append(summary)
                await progress_message.edit(content=f"Summarized website {idx}/{total_results}.")
            else:
                await progress_message.edit(content=f"Failed to summarize website {idx}/{total_results}.")
        else:
            await progress_message.edit(content=f"Failed to fetch content from website {idx}/{total_results}.")

    if not all_summaries:
        # If less than 10 URLs are successfully processed, perform another search
        if len(all_summaries) < 10:
            urls = perform_web_search(refined_query, start_index=len(urls)+1)
            # Repeat the summarization process for new URLs
            for idx, url in enumerate(urls[:10], start=1):
                content = fetch_website_content(url)

                if content:
                    context_for_summary = f"Original question: {topic}. Summarize this content in the context of this question."
                    summary = await summarize_content(content, context_for_summary)

                    if summary:
                        all_summaries.append(summary)
                        await progress_message.edit(content=f"Summarized website {idx}/{total_results}.")
                    else:
                        await progress_message.edit(content=f"Failed to summarize website {idx}/{total_results}.")
                else:
                    await progress_message.edit(content=f"Failed to fetch content from website {idx}/{total_results}.")

    if not all_summaries:
        await progress_message.edit(content="Failed to obtain usable summaries from search results.")
        return

    # Generate the final comprehensive response using GPT-4
    final_combined_summary = " ".join(all_summaries)
    context_for_final_response = f"Original question: {topic}. {final_combined_summary}"
    final_response = process_text_with_gpt(
        context_for_final_response,
        "Generate a comprehensive response based on this context.",
        gpt_version=4
    )

    await progress_message.edit(content="Research complete, generating response...")

    await send_large_message(interaction, f"**Original Question:** {topic}\n**Response:**\n{final_response}")
