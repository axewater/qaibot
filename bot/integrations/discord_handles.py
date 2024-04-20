# bot/integrations/discord_handles.py
import discord
import validators
from .openai_chat import ask_question, join_conversation, summarize_text, process_text_with_gpt
from ..utilities import send_large_message
from .summarize_url import fetch_website_content
from .google_search import perform_web_search

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
        summary = summarize_text(content, context_for_summary=f"Summarize the content at this URL: {url}")
        response_message = f"**SUMMARY OF:** {url}\n{summary if summary else 'Failed to generate a summary.'}"
        await send_large_message(interaction, response_message)
    else:
        await interaction.followup.send(f"Could not fetch or process content from the URL: {url}")


# Function for processing and responding to the imback command
async def handle_imback(interaction: discord.Interaction):
    await interaction.response.defer()

    channel = interaction.channel
    messages = await channel.history(limit=200).flatten()
    context = " ".join([msg.content for msg in messages[::-1]])  # Reverse for chronological order

    # Check if context exceeds 4000-token limit
    if len(context.split()) > 4000:
        await interaction.followup.send("Too much content to summarize (exceeds token limit).")
        return

    summary = summarize_text(context, context_for_summary="Summarize the last 200 messages for context.")

    if summary:
        await send_large_message(interaction, f"Summary of the last 200 messages:\n{summary}")
    else:
        await interaction.followup.send("Error: Could not generate a summary.")


# Function for processing and responding to the research command
async def handle_research(interaction: discord.Interaction, topic: str):
    await interaction.response.defer()

    await interaction.followup.send(f"Researching the topic: {topic}...")
    refined_query = process_text_with_gpt(
        topic,
        "This is a sentence typed by a human that we need to research online. Refine this topic into an effective web search query."
    )
    urls = perform_web_search(refined_query)

    summaries = []
    for url in urls[:5]:  # Limit to the top 5 results
        obfuscated_url = url.replace("http", "hxxp")
        content = fetch_website_content(url)
        if content:
            context_for_summary = f"Original question: {topic}. Please summarize this content in the context of this question."
            summary = summarize_text(content, context_for_summary)
            summaries.append(summary)
        else:
            await interaction.followup.send(f"Failed to fetch or summarize content from {obfuscated_url}")

    if not summaries:
        await interaction.followup.send("Failed to obtain usable summaries from search results.")
        return

    combined_summary = " ".join(summaries)
    context_for_final_response = f"Original question: {topic}. {combined_summary}"
    final_response = process_text_with_gpt(context_for_final_response, "Generate a comprehensive response based on this context.")

    await send_large_message(interaction, f"**Original Question:** {topic}\n**Response:**\n{final_response}")
