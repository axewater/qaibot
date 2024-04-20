# bot/integrations/discord_commands.py
import discord
from discord.ext import commands
import validators
from .openai_chat import ask_question, join_conversation, summarize_text, process_text_with_gpt
from ..utilities import send_large_message
from .summarize_url import summarize_text, fetch_website_content, process_text_with_gpt
from .google_search import perform_web_search

async def setup(bot):
    @bot.slash_command(name="qai", description="Ask QAI any question... it knows all!")
    async def qai(interaction: discord.Interaction, command_text: str):
        """Handles the slash command /qai."""
        
        
        await interaction.response.defer()
        print(f"Received question: {command_text}")
        
        processed_text = ask_question(command_text)
        if processed_text:
            
            await interaction.followup.send(processed_text)
        else:
            await interaction.followup.send("Error: No response received from processing.")
            
    @bot.slash_command(name="joinconvo", description="Let QAI join the conversation (reads last 15 messages).")
    async def joinconvo(interaction: discord.Interaction):
        """Handles the slash command /joinconvo."""
        await interaction.response.defer()

        print("Initiating join conversation command")
        channel = interaction.channel
        messages = await channel.history(limit=15).flatten()
        context = " ".join([msg.content for msg in messages[::-1]])  

        processed_text = join_conversation(context)
        if processed_text:
            await interaction.followup.send(processed_text)
        else:
            await interaction.followup.send("Error: No response generated.")
            
    @bot.slash_command(name="summarize", description="QAI will summarize the content of a given URL.")
    async def summarize(interaction: discord.Interaction, url: str):
        """Handles the slash command /summarize for a URL."""
        
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url

        
        if not validators.url(url):
            await interaction.response.send_message("The provided string is not a valid URL.")
            return

        await interaction.response.defer()
        content = fetch_website_content(url)
        if content:
            summary = summarize_text(content)
            
            response_message = f"**SUMMARY OF:** {url}\n{summary if summary else 'Failed to generate a summary.'}"
            await interaction.followup.send(response_message)
        else:
            await interaction.followup.send(f"Could not fetch or process content from the URL: {url}")        
            
            
    @bot.slash_command(name="research", description="Let QAI research a topic on the web for you.")
    async def research(interaction: discord.Interaction, topic: str):
        await interaction.response.defer()
        
        await interaction.followup.send("Transforming topic into a search query...")
        refined_query = process_text_with_gpt(topic, "Refine this topic into a web search query:")
        print(f"Refined search query: {refined_query}")
        await interaction.followup.send(f"Searching the web for: {refined_query}...")
        urls = perform_web_search(refined_query)
        print(f"Received URLs from search results: {urls}")
        summaries = []
        for url in urls[:5]:  # Limit to the top 5 results
            await interaction.followup.send(f"Summarizing content from {url}...")
            content = fetch_website_content(url)
            if content:
                summary = summarize_text(content)
                summaries.append(summary)
            else:
                await interaction.followup.send(f"Failed to fetch or summarize content from {url}")

        if not summaries:
            await interaction.followup.send("Failed to obtain usable summaries from search results.")
            return

        combined_summary = " ".join(summaries)
        await interaction.followup.send("Synthesizing the information gathered...")
        print("Combined summary:", combined_summary)
        final_response = process_text_with_gpt(combined_summary, "Provide a comprehensive answer or summary based on the information provided:")
        print("Final response:", final_response)

        await send_large_message(interaction, f"**Original Question:** {topic}\n**Response:**\n{final_response}")