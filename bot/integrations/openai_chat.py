# bot/integrations/openai_chat.py
import os
import logging
import traceback
from openai import OpenAI
import tiktoken
import time
import re
from ..integrations import summarize_url
from ..integrations import search_weather
from ..integrations import search_google
from ..integrations.search_imdb import search_imdb
from ..integrations.search_iptorrents import search_iptorrents as search_it_component
from ..integrations.search_steam import search_steam
from ..integrations.search_cdkeys import search_cdkeys
from ..integrations.search_magnetdl import search_torrents
from ..integrations.openai_imagegen import generate_image
from ..integrations.security_portscan import perform_port_scan
# from ..integrations.search_virustotal import search_virustotal_url, search_virustotal_domain, search_virustotal_ip


# Instantiate the OpenAI client with your API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TOKEN_LIMIT = 8000
DISCORD_LIMIT = 2000  # Maximum characters for Discord messages

RATE_LIMITS = {
     'gpt-3.5-turbo': {'tokens': 160000, 'requests': 5000},
     'gpt-4': {'tokens': 80000, 'requests': 5000},
     'gpt-4o': {'tokens': 600000, 'requests': 5000}
}

class RateLimiter:
    def __init__(self, limits):
        self.limits = limits
        self.requests = {key: 0 for key in limits.keys()}
        self.timestamps = {key: time.time() for key in limits.keys()}

    def check_request(self, model_name):
        current_time = time.time()
        elapsed = current_time - self.timestamps[model_name]
        if elapsed > 3600:
            self.requests[model_name] = 0
            self.timestamps[model_name] = current_time
        if self.requests[model_name] < self.limits[model_name]['requests']:
            self.requests[model_name] += 1
            return True
        return False

rate_limiter = RateLimiter(RATE_LIMITS)

def check_rate_limit(model_name):
    """Check if the request can be made within the rate limits."""
    can_proceed = rate_limiter.check_request(model_name)
    if not can_proceed:
        logging.warning(f"check_rate_limit: Rate limit exceeded for model {model_name}. Applying exponential back-off.")
        back_off_time = 1
        while not can_proceed:
            time.sleep(back_off_time)
            back_off_time *= 2  # Exponential increase
            can_proceed = rate_limiter.check_request(model_name)
            if back_off_time > 64:  # Cap the back-off time to prevent excessive waiting
                logging.error("check_rate_limit: Excessive back-off time. Aborting operation.")
                return False
    return True

def ask_question(question_text):
    logging.info("ask_question: Asking a question to GPT4")
    prompt = "You are QAI, a helpful Discord chatbot. Answer the following question. Do not translate any language to english. RETAIN THE LANGUAGE OF THE PROVIDED TEXT. Limit your output to 1000 characters."
    return process_text_with_gpt(question_text, prompt, gpt_version=4)


def magic_ai(question_text):
    logging.info("ask_question: Asking a question to GPT4 with tools in context")
    system_prompt = """
    The date of today is {date}.
    You are QAI, a helpful Discord chatbot that can use a variety of tools. 
    You will be asked a question, and you should first decide if the answer requires the use of your tools before answering.
    These are your tools and how to use them:
    {googlesearch:query}                    example : {googlesearch:"how to make a sandwich"}
    {summarize_url:url}                     example : {summarize_url:"https://example.com"}
    {imdbsearch:movie}                      example : {imdb:"The Matrix"}
    {it_component_search:component_name}    example : {it_component_search:"nvidia 4090"}
    {steamsearch:game_name}                 example : {steamsearch:"Grand Theft Auto V"}
    {cdkeysearch:game_name}                 example : {cdkeysearch:"GTA V"}
    {torrentsearch:game_name}               example : {torrentsearch:"Grand Theft Auto V"}
    {weather:location:when}                 examples : {weather:"London":now}, {weather:"London":tomorrow}, {weather:"London":week}
    {makeimage:prompt}                      example : {makeimage:"a cute dog"}
    {nmapscan:ip_address:ports}             example : {nmapscan:"237.84.2.178":"22,80,443"}
    
    To use a tool, just print the query as shown in the above examples. Only print that and wait for the answer.
    Then you will be returned the data from the tool, and you can use it to answer the original question from the user.
    """
    return process_magic_with_gpt(question_text, system_prompt, gpt_version=4)


def process_magic_with_gpt(question_text, system_prompt, gpt_version=4):
    logging.info(f"process_magic_with_gpt: Processing magic with GPT (version: " + str(gpt_version) + ")")

    # Send the user's question to process_text_with_gpt
    response = process_text_with_gpt(question_text, system_prompt, gpt_version) 


    # Define the regex pattern to match the commands
    pattern = r'\{(\w+):([^}]+)\}'

    # Find all the commands in the user's query
    commands = re.findall(pattern, response)

    # Process each command and store the results
    results = []
    for command, query in commands:
        if command == 'googlesearch':
            result = search_google(query)
        elif command == 'summarize_url':
            result = summarize_url(query)
        elif command == 'imdbsearch':
            result = search_imdb(query)
        elif command == 'it_component_search':
            result = search_it_component(query)
        elif command == 'steamsearch':
            result = search_steam(query)
        elif command == 'cdkeysearch':
            result = search_cdkeys(query)
        elif command == 'torrentsearch':
            result = search_torrents(query)
        elif command == 'weather':
            location, when = query.split(':')
            result = search_weather(location, when)
        elif command == 'makeimage':
            result = generate_image(query)
        elif command == 'nmapscan':
            ip_address, ports = query.split(':')
            result = perform_port_scan(ip_address, ports)
        else:
            result = f"Unknown command: {command}"

        results.append(result)

    # Combine the results into a single string
    combined_results = "\n".join(results)

    final_prompt =  """
                    You are QAI, a helpful Discord chatbot. You must a question from the user. I will provide you with context below. Try to limit your output to 1500 characters if it is possible without leaving out important details."
                    Question : {question_text}
                    Context : {combined_results}
                    """

    # Feed the combined results as context to GPT using process_text_with_gpt
    response = process_text_with_gpt(combined_results, final_prompt, gpt_version)

    return response

def report_weather(question_text, location, report_type="week"):
    logging.info(f"report_weather: Checking the weather API for a '{report_type}' report by GPT4")
    if report_type == "now":
        prompt = "Je bent QAI, een Discord weerbericht bot. Hier volgt de gegevens van het weerbericht van vandaag. Lees het voor als een nieuwsbericht. Beperkt de text tot een maximum van 300 karakters en gebruik veel emoticons."
    elif report_type == "tomorrow":
        prompt = "Je bent QAI, een Discord weerbericht bot. Hier volgt de gegevens van het weerbericht voor morgen. Lees het voor als een nieuwsbericht. Beperkt de text tot een maximum van 300 karakters en gebruik veel emoticons."
    else:
        prompt = "Je bent QAI, een Discord weerbericht bot. Hier volgt de gegevens van het weerbericht. Lees het voor als een 'week weer overzicht'. Beperkt de text tot een maximum van 500 karakters en gebruik veel emoticons."
    return process_text_with_gpt(question_text, prompt, gpt_version=4)

def join_conversation(context):
    logging.info("join_conversation: Joining the conversation with GPT4")
    prompt = "You are QAI, a nerdy Discord chatbot. Here is the recent conversation, join in using the dominant language of the conversation. Write a reply like a human. Limit your output to 200 characters."
    return process_text_with_gpt(context, prompt, gpt_version=4)

def summarize_text(text, context_for_summary="Please summarize this text to a maximum of 500 tokens. The text may be a snippet of a larger document, if all you see if a list of data, try to summarize the most essential part of the data, retaining its structure (data pairs) .Retain the source language of the material (NEVER TRANSLATE!)"):
    logging.info("summarize_text: Summarizing the text with GPT3")
    return process_text_with_gpt(text, context_for_summary, gpt_version=3)

def process_text_with_gpt(text, system_prompt, gpt_version=3):
    logging.info(f"process_text_with_gpt: Processing text with GPT (version: " + str(gpt_version) + ")")
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text}
    ]

    gpt_version_map = {
        4: "gpt-4o",
        3: "gpt-3.5-turbo"
    }

    model = gpt_version_map.get(gpt_version, "gpt-3.5-turbo")
    
    # Check rate limits before making the request
    if not check_rate_limit(model):
        logging.error("process_text_with_gpt: Failed to process text due to rate limiting.")
        return None

    # Tokenize the text and calculate the number of tokens
    tokenizer = tiktoken.get_encoding("cl100k_base")
    token_count = len(tokenizer.encode(text))
    logging.info(f"process_text_with_gpt: Token count for the request: {token_count}")

    try:
        response = client.chat.completions.create(
            messages=messages,
            model=model,
            max_tokens=4000,
            temperature=0.9
        )
        logging.info(f"process_text_with_gpt: GPT (version: " + str(gpt_version) + ") response completed.")
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"process_text_with_gpt: Error while calling OpenAI API:", e)
        logging.error(traceback.format_exc())
        return None
