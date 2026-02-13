import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Initialize the client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

try:
    print("Sending request to Gemini 2.0...")
    # Using the exact name from your list
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite", 
        contents="Hello! Confirm you are working as the AI Teaching Assistant."
    )
    
    print("-" * 30)
    print("AI Response:", response.text)
    print("-" * 30)

except Exception as e:
    print(f"An error occurred: {e}")