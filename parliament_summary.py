import requests
import os
from datetime import datetime, timedelta

# --- CONFIGURATION ---
# This pulls your Hugging Face token from the 'Secrets' we will set up next
HF_TOKEN = os.environ.get("HF_TOKEN") 
USER_EMAIL = "your-work-email@example.com" # OpenParliament asks for this in case of errors
KEYWORDS = ["labour market", "workforce development", "Future Skills Centre", "skills and training", "youth unemployment","Employment Social Development Canada"]
API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

def fetch_parliament_data():
   def fetch_parliament_data():
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    # Using the Lipad/OpenParliament style API structure
    url = f"https://api.openparliament.ca/hansards/?date={yesterday}"
    
    try:
        response = requests.get(url, headers={'Accept': 'application/json'}, timeout=10)
        if response.status_code == 200:
            data = response.json()
            objects = data.get('objects', [])
            
            # If no debates were held (like during a break), objects will be empty
            if not objects:
                return "No relevant mentions found."

            mentions = []
            for obj in objects:
                # We check if 'content_en' exists safely using .get()
                content = obj.get('content_en', "")
                if any(k.lower() in content.lower() for k in KEYWORDS):
                    mentions.append(content)
            
            return " ".join(mentions) if mentions else "No relevant mentions found."
        return "No relevant mentions found."
    except Exception as e:
        return f"Error fetching data: {str(e)}"

def query_summarizer(text):
    if not text.strip():
        return "No mentions of your keywords were found in Parliament yesterday."
    
    # We send the text to Hugging Face to be summarized
    # Models have a limit, so we take the first 3000 characters
    payload = {
        "inputs": text[:3000], 
        "parameters": {"max_length": 150, "min_length": 40, "do_sample": False}
    }
    response = requests.post(API_URL, headers=HEADERS, json=payload)
    
    if response.status_code == 200:
        return response.json()[0]['summary_text']
    else:
        return f"The AI is still waking up. (Error {response.status_code})"

if __name__ == "__main__":
    print("Fetching data from OpenParliament...")
    raw_content = fetch_parliament_data()
    print("Summarizing with AI...")
    summary = query_summarizer(raw_content)
    print("\n--- DAILY SKILLS & LABOUR BRIEFING ---")
    print(summary)
