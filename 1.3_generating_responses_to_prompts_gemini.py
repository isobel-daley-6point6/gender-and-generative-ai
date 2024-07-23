## Import Libraries & Load Environment Variables
import os
from dotenv import load_dotenv
from datetime import datetime
import json
from pathlib import Path
import sys

# Debug: Print current working directory and Python path
print("Current working directory:", os.getcwd())
print("Python path:", sys.path)

# Add scripts and data path to the list of search paths
script_dir = Path(os.path.dirname(os.path.abspath("__file__")))
sys.path.append(str(script_dir / "." / "src" / "scripts"))
sys.path.append(str(script_dir / "." / "data" / "products"))

# Import code to automate querying of Gemini AI
try:
    from gemini import QueryGemini
except ModuleNotFoundError as e:
    print("Error: ", e)
    sys.exit(1)

# Load environment variables from the .env file
# The .env file is where the "GEMINI_API_KEY" is stored
load_dotenv('.env')

# Import the GEMINI_API_KEY
api_key = os.environ.get('GEMINI_API_KEY')
if not api_key:
    print("Error: GEMINI_API_KEY not found in environment variables")
    sys.exit(1)

# Function to import products or roles dynamically
def import_list(module_name, list_name):
    try:
        module = __import__(module_name, fromlist=[list_name])
        return getattr(module, list_name)
    except ModuleNotFoundError as e:
        print("Error: ", e)
        sys.exit(1)

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

# Preview the selected list
print(f"{item_label.capitalize()}s:", prompt_list)

## Generate Responses
# Initiate query object
query_object = QueryGemini(api_key=api_key)

# Create empty list to store responses to the prompt
responses = []

# Generate responses based on the selected prompt type and number of iterations
print("Starting prompt generation...")
for iteration in range(iterations):
    print(f"Iteration: {iteration+1}/{iterations}")
    for item in prompt_list:
        # The search string specifies the prompt that is used
        search_string = search_string_template.format(item)
        print(f"Generating response for: {search_string}")
        response = query_object.connect_gemini(search_string=search_string)
        
        # Store the response to each prompt in a dictionary
        response_dict = {
            'timestamp': datetime.now().strftime("%Y%m%d%H%M%S"),
            item_label: item,
            'prompt': search_string,
            'response': response,
            'model': 'Gemini AI'
        }

        responses.append(response_dict)

print("Prompt generation completed.")

# Filter out errors and unwanted responses from the responses list
def cleanse_dicts(dicts):
    error_free_dicts = [d for d in dicts if isinstance(d.get("response"), str)]
    unwanted_responses = [
        "I'm Gemini, your creative and helpful collaborator.",
        "I have limitations and won't always get it right"
    ]
    cleansed_dicts = [d for d in error_free_dicts if not any(d.get("response").startswith(ur) for ur in unwanted_responses)]

    return cleansed_dicts

cleansed_responses = cleanse_dicts(responses)

# Convert dictionary to JSON
response_json = json.dumps(cleansed_responses, indent=4)

# Dump the JSON file
# Ensure the directory exists
output_path = Path("data/raw_data")
output_path.mkdir(parents=True, exist_ok=True)
output_file = output_path / f"gemini_responses_bulk_{prompt_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"

print(f"Saving responses to {output_file}")
with open(output_file, "w") as out_file:
    json.dump(response_json, out_file)

print("Script completed successfully.")