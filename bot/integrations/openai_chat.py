# bot/integrations/openai_chat.py
import os
import traceback
from openai import OpenAI

# Instantiate the OpenAI client with your API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def process_text_with_gpt(command_text):
    print("Processing text with GPT")
    systemprompt = "You are QAI, a helpful Discord chatbot. Answer questions, or just join the conversation printed."
    messages = [
        {"role": "system", "content": systemprompt},
        {"role": "user", "content": command_text}
    ]

    try:
        print("Sending the following request to OpenAI API: ", messages)
        # Using the new client method to create chat completions
        response = client.chat.completions.create(
            messages=messages,
            model="gpt-4-turbo",  # Change this to your preferred model
            max_tokens=2500,
            temperature=0.9
        )
        print("Received the following response: ", response)
        # Correctly accessing the response object's attributes
        return response.choices[0].message.content.strip()
    except Exception as e:
        print('Error while calling OpenAI API: ', e)
        print(traceback.format_exc())
        return None
