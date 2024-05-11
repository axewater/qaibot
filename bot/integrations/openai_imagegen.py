import sys
import os
import logging
import argparse
import json
from openai import OpenAI, BadRequestError

def generate_image(prompt, size='square', quality='standard'):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    logging.basicConfig(level=logging.INFO)
    
    size_options = {
        'square': '1024x1024',
        'tiktok': '1024x1792',
        'boomer': '1792x1024'
    }
    quality_options = {
        'standard': 'standard',
        'hd': 'hd'
    }
    
    selected_size = size_options.get(size)
    selected_quality = quality_options.get(quality)
    
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=selected_size,
            quality=selected_quality,
            n=1,
        )
        image_url = response.data[0].url
        result = {
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "url": image_url,
            "status": "success"
        }
    except BadRequestError as e:
        logging.error(f"Error generating image: {str(e)}")
        result = {
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "error": str(e),
            "status": "failed"
        }
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        result = {
            "prompt": prompt,
            "size": size,
            "quality": quality,
            "error": "An unexpected error occurred.",
            "status": "failed"
        }
    
    return json.dumps(result, indent=4)

def main():
    parser = argparse.ArgumentParser(description="Generate images using OpenAI's DALL-E model.")
    parser.add_argument('prompt', type=str, help='The prompt to generate the image for.')
    parser.add_argument('--size', type=str, choices=['square', 'tiktok', 'boomer'], default='square', help='Size of the generated image.')
    parser.add_argument('--quality', type=str, choices=['standard', 'hd'], default='standard', help='Quality of the generated image.')
    
    args = parser.parse_args()
    
    result = generate_image(args.prompt, args.size, args.quality)
    print(result)

if __name__ == "__main__":
    main()
