# bot/integrations/discord_commands.py
import discord
from discord.ext import commands
import validators
from .openai_chat import ask_question, join_conversation, summarize_text, process_text_with_gpt
from ..utilities import send_large_message
from .summarize_url import summarize_text, fetch_website_content, process_text_with_gpt
from .google_search import perform_web_search


# Function for processing and responding to the QAI command
async def handle_qai(interaction, question):
    await interaction.response.defer()
    print(f"Received question: {question}")

    processed_text = ask_question(question)
    if processed_text:
        await send_large_message(interaction, processed_text)
    else:
        await interaction.followup.send("Error: No response received from processing.")


# Function for processing and responding to the joinconvo command
async def handle_joinconvo(interaction):
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
async def handle_summarize(interaction, url):
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
async def handle_imback(interaction):
    await interaction.response.defer()

    channel = interaction.channel
    messages = await channel.history(limit=200).flatten()
    context = " ".join([msg.content for msg in messages[::-1]])  # Reverse for chronological order

    # Assuming 8000 tokens limit, check if context exceeds token limit
    if len(context.split()) > 8000:
        await interaction.followup.send("Too much content to summarize (exceeds token limit).")
        return

    summary = summarize_text(context, context_for_summary="Please summarize the last 200 messages.")

    if summary:
        await send_large_message(interaction, f"Summary of the last 200 messages:\n{summary}")
    else:
        await interaction.followup.send("Error: Could not generate a summary.")


# Function for processing and responding to the research command
async def handle_research(interaction, topic):
    await interaction.response.defer()

    # Step 1: Process topic into a refined search query
    await interaction.followup.send(f"Researching the topic: {topic}...")
    refined_query = process_text_with_gpt(
        topic,
        "This is a sentence typed by a human that we need to research online. Refine this topic into an effective web search query."
    )
    print(f"Refined search query: {refined_query}")

    # Step 2: Perform web search and fetch summaries
    urls = perform_web_search(refined_query)
    print(f"Received URLs from search results: {urls}")

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

    # Step 3: Handle case when no summaries are found
    if not summaries:
        await interaction.followup.send("Failed to obtain usable summaries from search results.")
        return

    # Step 4: Combine summaries and process final response
    combined_summary = " ".join(summaries)
    context_for_final_response = f"Original question: {topic}. {combined_summary}"
    final_response = process_text_with_gpt(context_for_final_response, "Generate a comprehensive response based on this context.")
    print("Final response:", final_response)

    # Step 5: Send the final message with original question and response
    await send_large_message(interaction, f"**Original Question:** {topic}\n**Response:**\n{final_response}")


# Setup function to add all slash commands to the bot
async def setup(bot):
    @bot.slash_command(name="qai", description="Ask QAI any question... it knows all!")
    async def qai(interaction: discord.Interaction, question: str):
        await handle_qai(interaction, question)

    @bot.slash_command(name="joinconvo", description="Let QAI join the conversation (reads last 15 messages).")
    async def joinconvo(interaction: discord.Interaction):
        await handle_joinconvo(interaction)

    @bot.slash_command(name="summarize", description="QAI will summarize the content of a given URL.")         
    async def summarize(interaction: discord.Interaction, url: str):
        await handle_summarize(interaction, url)

    @bot.slash_command(name="imback", description="I was away for a while, what happened while I was gone? Summarize the last 200 messages.")
    async def imback(interaction: discord.Interaction):
        await handle_imback(interaction)

    @bot.slash_command(name="research", description="Let QAI research a topic on the web for you.")
    async def research(interaction: discord.Interaction, topic: str):
        await handle_research(interaction, topic)