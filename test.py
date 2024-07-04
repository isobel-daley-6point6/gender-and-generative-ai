import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv('.env')
# Import the GEMINI_API_KEY
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')


response = model.generate_content("what is 1+1?")
print(response.text)

