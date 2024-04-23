# bot/commands/research.py
import discord
import validators
from ..utilities import send_large_message, summarize_content
from ..commands.qai import handle_qai
from ..commands.joinconvo import handle_joinconvo
from ..commands.pricewatch import handle_pricewatch
from ..commands.summarize import handle_summarize
from ..integrations.openai_chat import process_text_with_gpt
from ..integrations.google_search import perform_web_search
from ..integrations.summarize_url import fetch_website_content

# Function for processing and responding to the research command
async def handle_research(interaction: discord.Interaction, topic: str):
    await interaction.response.defer()

    progress_message = await interaction.followup.send("Initializing research...")

    # Refine the topic into an effective web search query using GPT-3.5
    refined_query = process_text_with_gpt(
        topic,
        "This is a sentence typed by a human that we need to research online. Refine this topic into an effective web search query without translating to another language. Keep English in English, Dutch in Dutch. etc.",
        gpt_version=3
    )

    await progress_message.edit(content=f"Researching the topic: {refined_query}...")

    # Perform a web search and get the actual number of results
    urls = perform_web_search(refined_query)

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
