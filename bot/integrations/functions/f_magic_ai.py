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
from bot.integrations.search_weather import search_weather
from bot.integrations.search_wikipedia import search_wikipedia
from bot.integrations.openai_imagegen import generate_image
from bot.commands.sectools.sshlogin import handle_sshlogin
from bot.commands.sectools.portscan import handle_portscan
from bot.integrations.search_virustotal import search_virustotal
from bot.integrations.openai_imageanalyze import get_image_description

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
            google_result = perform_web_search(query.strip('"'))
            # we get the list of URLs as a JSON, now we pass each of them to the summarize_url function
            summaries = []
            for url in google_result:
                summary = magic_summarize(url, query)
                summaries.append(summary)
            result = "\n".join(summaries)
        elif command == 'summarize_url':
            parts = query.split('"')
            if len(parts) >= 5:
                url = parts[1]
                context = parts[3]
                logging.info(f"process_magic_with_gpt: summarize_url URL: {url} Context: {context}")
                result = magic_summarize(url, context)
            else:
                result = "Invalid summarize_url command format. Expected: [summarize_url:\"http://example.com\":\"context\"]"
        elif command == 'wikipedia':
            query, country = query.split(':')
            logging.info(f"process_magic_with_gpt: WIKI Query: {query} Country: {country} ")
            result = search_wikipedia(query.strip('"'), 5, country.strip('"'))        
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
            # Split the query to handle multiple parameters
            location, when = query.split(':')
            result = search_weather(location.strip('"'), when)
        elif command == 'makeimage':
            result = generate_image(query)
        elif command == 'analyzeimage':
            result = get_image_description(query.strip('"'))
        elif command == 'portscanner':
            ip_address, ports = query.split(':')
            result = handle_portscan(ip_address.strip('"'), ports.strip('"'))
        elif command == 'testssh':
            ip_address, port = query.split(':')
            logging.info(f"process_magic_with_gpt: testssh IP: {ip_address} Port: {port} ")
            logging.info(f"process_magic_with_gpt: testssh parsing IP: {ip_address} Port: {port} " % (ip_address.strip('"'), (port.strip('"'))))
            result = handle_sshlogin(ip_address.strip('"'), (port.strip('"')))
        elif command == 'virustotal':
            # Split the query to handle multiple parameters
            logging.info(f"process_magic_with_gpt: Splitting VT query: {query} ")
            vt_query, vt_type = query.split(':')
            vt_query = vt_query.strip('"')
            vt_type = vt_type.strip('"')
            result = search_virustotal(vt_query, vt_type)
        else:
            result = f"Unknown command: {command}"

        results.append(result)

    # Combine the results into a single string
    combined_results = "\n".join(map(str, results))

    final_prompt = """
    You are QAI, a helpful Discord chatbot. You must answer a question from the user. I will provide you with context below.

    Here are some rules about how you MUST reply in certain cases :
    
    -If the Context appears to be a weather report, you shall read it like a news report and use maximum amount of emoticons for decoration in the Discord message.
    -If the Context appears to be a port scan report, you shall read it like a pentest report and use maximum amount of emoticons for decoration in the Discord message.
    -If the Question allows, you will reply with a lot of emoticons for decoration in the Discord message.
    -Modify your response length according to the Question.
    
    
    Question: {question_text}
    Context: {combined_results}
    """.format(question_text=question_text, combined_results=combined_results)

    logging.info(f"process_magic_with_gpt: Processing Final prompt: {final_prompt}")
    # Feed the combined results as context to GPT using process_text_with_gpt
    response = process_text_with_gpt(combined_results, final_prompt, gpt_version)

    return response
