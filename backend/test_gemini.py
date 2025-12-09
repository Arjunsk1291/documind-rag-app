import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

print("Testing Gemini 2.5 Flash...")
model = genai.GenerativeModel('models/gemini-2.5-flash')

try:
    response = model.generate_content("Hello! Say 'Hi' back in one word.")
    print(f"✅ Success! Response: {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\nTesting text-embedding-004...")
try:
    result = genai.embed_content(
        model="models/text-embedding-004",
        content="This is a test",
        task_type="retrieval_document"
    )
    print(f"✅ Success! Embedding dimension: {len(result['embedding'])}")
except Exception as e:
    print(f"❌ Error: {e}")
