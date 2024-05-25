# bot/integrations/openai_chat.py
import os
import logging
import traceback
from openai import OpenAI
import tiktoken
import time
import sys




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

def ask_question(question_text, context=None):
    logging.info("ask_question: Asking a question to GPT4")
    prompt = "Jij bent QAI, een helpzame, nerdy Discord chatbot. Antwoord altijd in de bron tool. Beantwoord de volgende vraag, en limiteer jezelf tot 1000 karakters."
    return process_text_with_gpt(question_text, prompt, gpt_version=4)



def report_weather(question_text, location, report_type="week"):
    logging.info(f"report_weather: Checking the weather for location '{location}' with  '{report_type}' report by GPT4 with question text: {question_text}")
    if report_type == "now":
        prompt = f"Je bent QAI, een Discord weerbericht bot. Hier volgen de gegevens van het weerbericht van vandaag voor de locatie: {location}. Lees het voor als een nieuwsbericht. Beperkt de text tot een maximum van 300 karakters en gebruik veel emoticons."
    elif report_type == "tomorrow":
        prompt = f"Je bent QAI, een Discord weerbericht bot. Hier volgen de gegevens van het weerbericht voor morgen voor de locatie: {location}. Lees het voor als een nieuwsbericht. Beperkt de text tot een maximum van 300 karakters en gebruik veel emoticons."
    else:
        prompt = f"Je bent QAI, een Discord weerbericht bot. Hier volgen de gegevens van het weerbericht voor de locatie: {location} voor de komende 7 dagen. Lees het voor als een 'week weer overzicht'. Beperkt de text tot een maximum van 500 karakters en gebruik veel emoticons."
    return process_text_with_gpt(question_text, prompt, gpt_version=4)


def join_conversation(context):
    logging.info("join_conversation: Joining the conversation with GPT4")
    prompt = "Jij bent QAI, een nerdy Discord chatbot. Hier is een stuk van de recente conversatie. Doe mee in het gesprek alsof je een mens bent (join in). Gebruik veel emoticons en limiteer je output tot 250 karakters."
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
