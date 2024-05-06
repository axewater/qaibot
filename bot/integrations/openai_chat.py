# bot/integrations/openai_chat.py
import os, logging, traceback
from openai import OpenAI

# Instantiate the OpenAI client with your API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_question(question_text):
    logging.info("ask_question: Asking a question to GPT4")
    prompt = "You are QAI, a helpful Discord chatbot. Answer the following question. Do not translate any language to english. RETAIN THE LANGUAGE OF THE PROVIDED TEXT. Limit your output to 1000 characters."
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
        4: "gpt-4-turbo",
        3: "gpt-3.5-turbo"
    }

    model = gpt_version_map.get(gpt_version, "gpt-3.5-turbo")
    
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
        logging.error(f"Error while calling OpenAI API:", e)
        logging.error(traceback.format_exc())
        return None
