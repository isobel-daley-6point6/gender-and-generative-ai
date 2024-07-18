import requests
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv('.env')

# Import the CLAUDE_API_KEY
api_key = os.environ.get('CLAUDE_API_KEY')
if not api_key:
    print("Error: CLAUDE_API_KEY not found in environment variables")
    exit(1)

def test_claude_api(api_key):
    url = "https://api.anthropic.com/v1/complete"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01"
    }
    payload = {
        "model": "claude-3.5-sonnet-20240620",  # Example model version
        "prompt": "\n\nHuman: Test prompt\n\nAssistant:",
        "max_tokens": 100,
        "temperature": 0.7,
        "top_p": 1
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        print("API Key is working. Response received:")
        print(data)
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except Exception as err:
        print(f"Other error occurred: {err}")

# Test the API key
test_claude_api(api_key)