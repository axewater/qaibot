import logging
import re, sys
from bot.integrations.search_google import perform_web_search
from bot.integrations.openai_chat import process_text_with_gpt
from bot.integrations.search_imdb import search_imdb
from bot.integrations.search_marktplaats import scrape_marktplaats_items
from bot.integrations.search_iptorrents import search_iptorrents
from bot.integrations.search_pricewatch import search_tweakers_pricewatch
from bot.integrations.search_steam import search_steam
from bot.integrations.search_cdkeys import search_cdkeys
import bot.integrations.search_weather as search_weather
from bot.integrations.security_portscan import perform_port_scan
from bot.integrations.openai_imagegen import generate_image

sys.path.append('/bot/integrations') 

try:
    from integrations.summarize_url import magic_summarize
except ImportError:
    from summarize_url import magic_summarize


def process_magic_with_gpt(question_text, system_prompt, gpt_version=4):
    logging.info(f"process_magic_with_gpt: Question: {question_text} ")

    # Send the user's question to process_text_with_gpt
    response = process_text_with_gpt(question_text, system_prompt, gpt_version) 
    logging.info(f"process_magic_with_gpt: Response: {response} ")
    # Define the regex pattern to match the commands
    pattern = r'\[(\w+):([^\]]+)\]'

    # Find all the commands in the user's query
    commands = re.findall(pattern, response)
    logging.info(f"process_magic_with_gpt: Found {len(commands)} commands: {commands}")
    # Process each command and store the results
    results = []
    for command, query in commands:
        logging.info(f"process_magic_with_gpt: Processing command: {command} with query: {query}")
        if command == 'googlesearch':
            result = perform_web_search(query)
        elif command == 'summarize_url':
            result = magic_summarize(query)
        elif command == 'imdbsearch':
            result = search_imdb(query)
        elif command == 'marktplaats':
            result = scrape_marktplaats_items(query)
        elif command == 'iptorrents':
            result = search_iptorrents(query)
        elif command == 'it_component_search':
            result = search_tweakers_pricewatch(query)
        elif command == 'steamsearch':
            result = search_steam(query)
        elif command == 'cdkeysearch':
            result = search_cdkeys(query)
        elif command == 'weather':
            result = search_weather(query)
        elif command == 'makeimage':
            result = generate_image(query)
        elif command == 'nmapscan':
            result = perform_port_scan(query)
        else:
            result = f"Unknown command: {command}"

        results.append(result)

    # Combine the results into a single string
    combined_results = "\n".join(map(str, results))

    final_prompt = """
    You are QAI, a helpful Discord chatbot. You must answer a question from the user. I will provide you with context below.

    Question: {question_text}
    Context: {combined_results}
    """.format(question_text=question_text, combined_results=combined_results)

    logging.info(f"process_magic_with_gpt: Processing Final prompt: {final_prompt}")
    # Feed the combined results as context to GPT using process_text_with_gpt
    response = process_text_with_gpt(combined_results, final_prompt, gpt_version)

    return response
