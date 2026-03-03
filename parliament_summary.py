import requests
import os
from datetime import datetime, timedelta

# --- CONFIGURATION ---
# This pulls your Hugging Face token from the 'Secrets' we will set up next
HF_TOKEN = os.environ.get("HF_TOKEN") 
USER_EMAIL = "your-work-email@example.com" # OpenParliament asks for this in case of errors
KEYWORDS = ["labour market", "workforce development", "Future Skills Centre", "skills and training"]
API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

def fetch_parliament_data():
    # Looks for data from the previous day
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    combined_text = ""
    
    for word in KEYWORDS:
        # Search OpenParliament debates
        url = f"https://api.openparliament.ca/debates/?q={word}&date={yesterday}"
        res = requests.get(url, headers={'User-Agent': USER_EMAIL, 'Accept': 'application/json'})
        
        if res.status_code == 200:
            data = res.json()
            for obj in data.get('objects', []):
                # Clean up the text slightly for the AI
                content = obj['content_en'].replace('\n', ' ')
                combined_text += f" [Topic: {word}] {content}\n"
    
    return combined_text

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
