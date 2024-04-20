# bot/integrations/openai_chat.py
import os
import traceback
from openai import OpenAI

# Instantiate the OpenAI client with your API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_question(question_text):
    print("Asking a question to GPT")
    prompt = "You are QAI, a helpful Discord chatbot. Answer the following question."
    return process_text_with_gpt(question_text, prompt)

def join_conversation(context):
    print("Joining the conversation with GPT")
    prompt = "You are QAI, a nerdy Discord chatbot. Here is the recent conversation, join in."
    return process_text_with_gpt(context, prompt)

def summarize_text(text, context_for_summary="Please summarize this text to a maximum of 1000 tokens."):
    print("Summarizing the text with GPT")
    return process_text_with_gpt(text, context_for_summary)

def process_text_with_gpt(text, system_prompt):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text}
    ]

    try:
        # print("Sending the following request to OpenAI API: ", messages)
        response = client.chat.completions.create(
            messages=messages,
            model="gpt-4-turbo",  # Adjust model as needed
            max_tokens=4000,
            temperature=0.9
        )
        # print("Received the following response: ", response)
        return response.choices[0].message.content.strip()
    except Exception as e:
        print('Error while calling OpenAI API: ', e)
        print(traceback.format_exc())
        return None
