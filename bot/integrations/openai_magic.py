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
    
def magic_ai(question_text, context=None):
    logging.info(f"magic_ai: START Asking a question to GPT4 with tools in context. Question: {question_text}")
    
    # Get the current date in a human-readable format
    current_date = datetime.now().strftime("%B %d, %Y")
    
    system_prompt = f"""
    The date of today is {current_date}.
    You are an AI trained by OpenAI and you knowledge cut-off date is january 1, 2023.
    You play the role of QAI, a helpful Discord chatbot that can use a variety of tools. 
    You will be asked a question, and you should first decide if the answer requires the use of your tools before answering.
    
    These are your tools and how to use them:
    [googlesearch:query]                    example : [googlesearch:"how to make a sandwich"]
    this will return a list of URLs. use this for requests about recent information beyond your knoewledge cut-off date
    
    [summarize_url:url]                     example : [summarize_url:"https://example.com"]
    this will return a summary of the URL
    
    [imdbsearch:movie]                      example : [imdb:"The Matrix"]
    this will return a list of movie names with IMDB URLs and ratings
    
    [it_component_search:component_name]    example : [it_component_search:"nvidia 4090"]
    this will return a list of IT components with current prices
    
    [marktplaats:product_name]               example : [marktplaats]:"gucci tassen"]
    this will return a list matching products offered second hand. Can be used for : Just about anything
    
    [steamsearch:game_name]                 example : [steamsearch:"Grand Theft Auto V"]
    this will return a list matching games with Steam URLs with prices.
    
    [cdkeysearch:game_name]                 example : [cdkeysearch:"GTA V"]
    this will return a list matching games with cheap cdkeys with prices. Much cheaper than Steam.
    
    [torrentsearch:title_name]               example : [torrentsearch:"Grand Theft Auto V"]
    this will return a list matching titles with torrent links. Can be used for : Movies, Series, Games, Software, etc
    
    [weather:location:when]                 examples : [weather:"London":now], [weather:"London":tomorrow], [weather:"London":week]
    this will return weather data for the given location and time. Note that time only has 3 options.
    
    [makeimage:prompt]                      example : [makeimage:"a cute dog"]
    use this when asked to create an image
    
    [nmapscan:ip_address:ports]             example : [nmapscan:"237.84.2.178":"22,80,443"]
    use this for securiy checks when asked. or when you need to explore a host further for recon.
    
    To use a tool, just print the query as shown in the above examples. Only print that and wait for the answer.
    Then you will be returned the data from the tool, and you can use it to answer the original question from the user.
    """
    logging.info(f"magic_ai: Magic System prompt: {system_prompt}")
    return process_magic_with_gpt(question_text, system_prompt, gpt_version=4)
