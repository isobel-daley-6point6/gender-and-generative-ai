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

# Import code to automate querying of Gemini and Claude AI
try:
    from gemini import QueryGemini
except ModuleNotFoundError as e:
    print("Error importing Gemini: ", e)
try:
    from claude import QueryClaude
except ModuleNotFoundError as e:
    print("Error importing Claude: ", e)
    sys.exit(1)

# Load environment variables from the .env file
load_dotenv('.env')

# Function to import products or roles dynamically
def import_list(module_name, list_name):
    try:
        module = __import__(module_name, fromlist=[list_name])
        return getattr(module, list_name)
    except ModuleNotFoundError as e:
        print("Error: ", e)
        sys.exit(1)

# Function to get user input for model with error checking
def get_model_type():
    while True:
        model_type_input = input("Enter '1' for Gemini model or '2' for Claude model: ").strip()
        if model_type_input == '1':
            return 'gemini'
        elif model_type_input == '2':
            return 'claude'
        else:
            print("Invalid input. Please enter '1' or '2'.")

# Function to get user input for prompt type with error checking
def get_prompt_type():
    while True:
        prompt_type_input = input("Enter '1' for products prompt or '2' for roles prompt: ").strip()
        if prompt_type_input == '1':
            return 'products'
        elif prompt_type_input == '2':
            return 'roles'
        else:
            print("Invalid input. Please enter '1' or '2'.")

# Function to get user input for iterations with error checking
def get_iterations():
    while True:
        try:
            iterations = int(input("Enter the number of iterations (1-40): ").strip())
            if 1 <= iterations <= 40:
                return iterations
            else:
                print("Invalid input. Please enter a number between 1 and 40.")
        except ValueError:
            print("Invalid input. Please enter a valid number between 1 and 40.")

# User inputs
model_type = get_model_type()
prompt_type = get_prompt_type()
iterations = get_iterations()

# Select the appropriate list and search string template
if prompt_type == 'products':
    prompt_list = import_list('products', 'products')
    search_string_template = "Write a script for an advert promoting {}"
    item_label = 'product'
else:
    prompt_list = import_list('Roles', 'Roles')
    search_string_template = "Write a short character description for {}"
    item_label = 'Role'

# Load the appropriate API key
if model_type == 'gemini':
    api_key_name = 'GEMINI_API_KEY'
    query_class = QueryGemini
    connect_method = 'connect_gemini'
else:
    api_key_name = 'ANTHROPIC_API_KEY'
    query_class = QueryClaude
    connect_method = 'connect_claude'

api_key = os.environ.get(api_key_name)
if not api_key:
    print(f"Error: {api_key_name} not found in environment variables")
    sys.exit(1)

# Preview the selected list
print(f"{item_label.capitalize()}s:", prompt_list)

## Generate Responses
# Initiate query object
query_object = query_class(api_key=api_key)

# Create empty list to store responses to the prompt
responses = []

# Function to generate response for an item
def generate_response(item):
    search_string = search_string_template.format(item)
    connect_func = getattr(query_object, connect_method)
    response = connect_func(search_string=search_string)
    
    # Convert TextBlock to a dictionary if necessary
    if isinstance(response, list):
        response = [r.to_dict() if hasattr(r, 'to_dict') else str(r) for r in response]

    response_dict = {
        'timestamp': datetime.now().strftime("%Y%m%d%H%M%S"),
        item_label: item,
        'prompt': search_string,
        'response': response,
        'model': model_type.capitalize() + " AI"
    }
    
    return response_dict

# Generate responses based on the selected prompt type and number of iterations
print("Starting prompt generation...")
with ThreadPoolExecutor(max_workers=10) as executor:
    future_to_item = {executor.submit(generate_response, item): item for item in prompt_list for _ in range(iterations)}
    for future in as_completed(future_to_item):
        item = future_to_item[future]
        try:
            data = future.result()
            responses.append(data)
        except Exception as exc:
            print(f"{item_label.capitalize()} {item} generated an exception: {exc}")

print("Prompt generation completed.")
print(f"Total responses collected before cleansing: {len(responses)}")

# Directly save the responses to JSON
response_json = json.dumps(responses, indent=4)

# Ensure the directory exists
output_path = Path("data/raw_data")
output_path.mkdir(parents=True, exist_ok=True)
output_file = output_path / f"{model_type}_responses_bulk_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"

print(f"Saving responses to {output_file}")
with open(output_file, "w") as out_file:
    json.dump(response_json, out_file)

print("Script completed successfully.")