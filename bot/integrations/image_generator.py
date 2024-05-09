import sys
import os
import logging
import base64
import openai

# Set up basic logging
logging.basicConfig(level=logging.INFO)

def generate_image(prompt):
    logging.info("Generating an image from OpenAI.")
    # Ensure the API key is set in your environment variables
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai.api_key:
        logging.error("No API key found in environment variables.")
        return None

    try:
        # Request the API to create an image
        response = openai.Image.create(prompt=prompt, n=1)
        # Assume the API returns a single image in base64
        image_data = response['data'][0]['url']
        file_path = 'generated_image.jpg'
        with open(file_path, 'wb') as file:
            file.write(base64.b64decode(image_data))
        logging.info("Image generated and saved at " + file_path)
        return file_path
    except Exception as e:
        logging.error(f"Failed to generate image: {e}")
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python image_generator.py 'prompt'")
        return
    prompt = sys.argv[1]
    result = generate_image(prompt)
    if result:
        print(f"Image successfully generated and saved at {result}")
    else:
        print("Failed to generate image.")

if __name__ == "__main__":
    main()
