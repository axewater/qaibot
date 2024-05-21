import os
import sys
import logging
from datetime import datetime

# Dynamically add the bot directory to the Python path
sys.path.append('/bot/integrations/functions')  # Ensures the functions directory is in the path

try:
    from bot.integrations.functions.f_magic_ai import process_magic_with_gpt
except ImportError:
    from .functions.f_magic_ai import process_magic_with_gpt
    
def magic_ai(question_text):
    logging.info(f"magic_ai: START Asking a question to GPT4 with tools in context. Question: {question_text}")
    
    # Get the current date in a human-readable format
    current_date = datetime.now().strftime("%B %d, %Y")
    
    system_prompt = f"""
    The date of today is {current_date}.
    You are an AI trained by OpenAI and you knowledge cut-off date is january 1, 2024.
    You play the role of QAI, a helpful Discord chatbot that can use a variety of tools. 
    You will be asked a question, and you should first decide if the answer requires the use of your tools before answering.
    
    These are your tools and how to use them:
    [googlesearch:query]                    example : [googlesearch:"how to make a sandwich"]
    [summarize_url:url]                     example : [summarize_url:"https://example.com"]
    [imdbsearch:movie]                      example : [imdb:"The Matrix"]
    [it_component_search:component_name]    example : [it_component_search:"nvidia 4090"]
    [steamsearch:game_name]                 example : [steamsearch:"Grand Theft Auto V"]
    [cdkeysearch:game_name]                 example : [cdkeysearch:"GTA V"]
    [torrentsearch:game_name]               example : [torrentsearch:"Grand Theft Auto V"]
    [weather:location:when]                 examples : [weather:"London":now], [weather:"London":tomorrow], [weather:"London":week]
    [makeimage:prompt]                      example : [makeimage:"a cute dog"]
    [nmapscan:ip_address:ports]             example : [nmapscan:"237.84.2.178":"22,80,443"]
    
    To use a tool, just print the query as shown in the above examples. Only print that and wait for the answer.
    Then you will be returned the data from the tool, and you can use it to answer the original question from the user.
    """
    logging.info(f"magic_ai: Magic System prompt: {system_prompt}")
    return process_magic_with_gpt(question_text, system_prompt, gpt_version=4)
