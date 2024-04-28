# bot/commands/research.py
import discord
import os
from ..utilities import send_large_message, summarize_content
from ..integrations.openai_chat import process_text_with_gpt
from ..integrations.google_search import perform_web_search
from ..integrations.summarize_url import fetch_website_content
from .blacklist import load_blacklist

MAX_SUMMARIES = 10


async def handle_research(interaction: discord.Interaction, topic: str, depth: str = 'normal'):
    await interaction.response.defer()

    progress_message = await interaction.followup.send("Initializing research...")

    depth_mapping = {'quick': 3, 'normal': 10, 'deep': 25}
    max_summaries = depth_mapping.get(depth, 10)
    print(f"handle_research: Will loop through search {max_summaries} times.")
    blacklist_filename = 'blacklist_urls.json'
    blacklist = load_blacklist(blacklist_filename)

    refined_query = process_text_with_gpt(
        topic,
        "This is a sentence typed by a human that we need to research online. Refine this topic into an effective web search query without translating to another language. Keep English in English, keep Dutch in Dutch. etc.",
        gpt_version=3
    )
    print(f"handle_research: Searching for '{refined_query}' with depth '{depth}'")
    await progress_message.edit(content=f"Researching the topic: {refined_query}...")

    urls = perform_web_search(refined_query, max_results=max_summaries)

    urls = [url for url in urls if url not in blacklist]

    total_results = len(urls)
    all_summaries = []

    for idx, url in enumerate(urls, start=1):
        print(f"handle_research: Processing website {idx}/{max_summaries}...")
        content = fetch_website_content(url)

        if content:
            context_for_summary = f"Original question: {topic}. Summarize this content in the context of this question."
            summary = await summarize_content(content, context_for_summary)

            if summary:
                all_summaries.append(summary)
                await progress_message.edit(content=f"Summarized website {idx}/{max_summaries}.")
            else:
                await progress_message.edit(content=f"Failed to summarize website {idx}/{max_summaries}.")
        else:
            await progress_message.edit(content=f"Failed to fetch content from website {idx}/{max_summaries}.")

    if not all_summaries:
        await progress_message.edit(content="Failed to obtain usable summaries from search results.")
        return

    print("Web search complete, processing summaries...")
    final_combined_summary = " ".join(all_summaries)
    print("Summaries processed, generating final response...")
    context_for_final_response = f"Original question: {topic}. {final_combined_summary}"
    print("Generating final response...")
    final_response = process_text_with_gpt(
        context_for_final_response,
        "Generate a comprehensive response based on this context.",
        gpt_version=4
    )
    print("Final response generated")
    await progress_message.edit(content="Research complete, generating response...")
    
    print("End of research")
    await send_large_message(interaction, f"**Original Question:** {topic}\n**Response:**\n{final_response}")
