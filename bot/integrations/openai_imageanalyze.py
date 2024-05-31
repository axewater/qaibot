import argparse
import json
import requests
import os

API_ENDPOINT = "https://api.openai.com/v1/chat/completions"
api_key = os.getenv("OPENAI_API_KEY")

def get_image_description(image_url, api_key=api_key):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": "gpt-4-turbo",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Describe this image in detail."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }

    response = requests.post(API_ENDPOINT, headers=headers, data=json.dumps(data))
    response.raise_for_status()

    return response.json()["choices"][0]["message"]["content"].strip()

def main():
    parser = argparse.ArgumentParser(description="Send an image URL to OpenAI and get a description.")
    parser.add_argument("image_url", help="The URL of the image to analyze.")

    args = parser.parse_args()

    try:
        description = get_image_description(args.image_url, api_key)
        print(description)
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()