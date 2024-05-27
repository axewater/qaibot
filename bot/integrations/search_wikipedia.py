import argparse
import json
import wikipedia

def search_wikipedia(query, num_results, country):
    wikipedia.set_lang(country)
    search_results = wikipedia.search(query, results=num_results)
    
    if search_results:
        output = []
        
        # Retrieve full details of the first result
        first_page = wikipedia.page(search_results[0])
        first_result = {
            "title": first_page.title,
            "url": first_page.url,
            "summary": first_page.summary,
            "content": first_page.content
        }
        output.append(first_result)
        
        # Retrieve summaries of the next 4 results
        for result in search_results[1:5]:
            try:
                page = wikipedia.page(result)
                result_data = {
                    "title": page.title,
                    "url": page.url,
                    "summary": page.summary
                }
                output.append(result_data)
            except wikipedia.exceptions.PageError:
                # Skip pages that cannot be found
                continue
        
        # Output the results in JSON format
        json_output = json.dumps(output, indent=2)
        print(json_output)
        return json_output
    else:
        print(f"No results found for '{query}'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search and retrieve articles from Wikipedia.")
    parser.add_argument("query", help="The search query.")
    parser.add_argument("-l", "--country", default="en", help="The country code for Wikipedia (default: 'en' for English).")
    
    args = parser.parse_args()
    
    search_wikipedia(args.query, num_results=5, country=args.country)