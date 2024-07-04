# src/scripts/gemini.py

import google.generativeai as genai

class QueryGemini:
    def __init__(self, api_key):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def connect_gemini(self, search_string):
        try:
            print(f"Generating content for prompt: {search_string}")
            response = self.model.generate_content(search_string)
            return response.text if response else None
        except Exception as e:
            print(f"Request failed: {e}")
            return str(e)