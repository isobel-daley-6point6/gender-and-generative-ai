# src/scripts/claude.py

from anthropic import Anthropic

class QueryClaude:
    def __init__(self, api_key):
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-3-opus-20240229"

    def connect_claude(self, search_string):
        try:
            print(f"Generating content for prompt: {search_string}")
            response = self.client.messages.create(
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": search_string,
                    }
                ],
                model=self.model,
            )
            if response:
                print(f"Response received: {response.content}")
            return response.content if response else None
        except Exception as e:
            print(f"Request failed: {e}")
            return str(e)