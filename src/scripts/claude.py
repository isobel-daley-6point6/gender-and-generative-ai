import requests

class QueryClaude:
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = "https://api.anthropic.com/v1/complete"  # Correct endpoint for Claude

    def connect_claude(self, search_string):
        headers = {
            "Authorization": f"Bearer {self.api_key}",  # Use the correct header
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"  # Required API version header
        }
        payload = {
            "model": "claude-3.5-sonnet-20240620",  # Example model version
            "prompt": f"\n\nHuman: {search_string}\n\nAssistant:",
            "max_tokens": 1000,
            "temperature": 0.7,
            "top_p": 1
        }
        try:
            print(f"Generating content for prompt: {search_string}")
            response = requests.post(self.url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json().get('completion')
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")  # Improved error logging
        except Exception as e:
            print(f"Other error occurred: {e}")
        return None