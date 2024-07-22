## Import Libraries & Load Environment Variables
import os
from dotenv import load_dotenv
from datetime import datetime
import json
from pathlib import Path
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

# Debug: Print current working directory and Python path
print("Current working directory:", os.getcwd())
print("Python path:", sys.path)

# Add scripts and data path to the list of search paths
script_dir = Path(os.path.dirname(os.path.abspath("__file__")))
sys.path.append(str(script_dir / "." / "src" / "scripts"))
sys.path.append(str(script_dir / "." / "data" / "products"))

# Import code to automate querying of Claude AI
try:
    from claude import QueryClaude
except ModuleNotFoundError as e:
    print("Error: ", e)
    sys.exit(1)

# Import list of products
try:
    from products import products
except ModuleNotFoundError as e:
    print("Error: ", e)
    sys.exit(1)

# Load environment variables from the .env file
# The .env file is where the "ANTHROPIC_API_KEY" is stored
load_dotenv('.env')

# Import the ANTHROPIC_API_KEY
api_key = os.environ.get('ANTHROPIC_API_KEY')
if not api_key:
    print("Error: ANTHROPIC_API_KEY not found in environment variables")
    sys.exit(1)

# Preview list of products
print("Products:", products)

## Generate Responses
# Initiate query object
query_object = QueryClaude(api_key=api_key)

# Create empty list to store responses to the prompt
responses = []

# Function to generate response for a product
def generate_response(product):
    search_string = f"Write a script for an advert promoting {product}"
    # print(f"Generating response for: {search_string}")
    response = query_object.connect_claude(search_string=search_string)
    
    # if response:
    #     print(f"Response received for {product}: {response}")
    # else:
    #     print(f"No response received for {product}")

    # Convert TextBlock to a dictionary if necessary
    if isinstance(response, list):
        response = [r.to_dict() if hasattr(r, 'to_dict') else str(r) for r in response]

    response_dict = {
        'timestamp': datetime.now().strftime("%Y%m%d%H%M%S"),
        'product': product,
        'prompt': search_string,
        'response': response,
        'model': 'Claude AI'
    }
    
    return response_dict

# The prompt is run 40 times for each product
print("Starting prompt generation...")
with ThreadPoolExecutor(max_workers=10) as executor:
    future_to_product = {executor.submit(generate_response, product): product for product in products for _ in range(40)}
    for future in as_completed(future_to_product):
        product = future_to_product[future]
        try:
            data = future.result()
            responses.append(data)
        except Exception as exc:
            print(f"Product {product} generated an exception: {exc}")

print("Prompt generation completed.")
print(f"Total responses collected before cleansing: {len(responses)}")

# Directly save the responses to JSON without cleansing for debugging
response_json = json.dumps(responses, indent=4)

# Debug: Print JSON data to be saved
# print(f"JSON data to be saved: {response_json}")

# Dump the JSON file
# Ensure the directory exists
output_path = Path("data/raw_data")
output_path.mkdir(parents=True, exist_ok=True)
output_file = output_path / f"claude_responses_bulk_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"

print(f"Saving responses to {output_file}")
with open(output_file, "w") as out_file:
    json.dump(response_json, out_file)

print("Script completed successfully.")