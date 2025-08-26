import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from openai import OpenAI
from langdetect import detect
from pymongo import MongoClient
from datetime import datetime, timezone

# -------------------------
# MongoDB connection
# -------------------------
mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["chatbot_db"]
collection = db["conversations"]

# -------------------------
# OpenAI client (replace with your actual API key)
# -------------------------
client = OpenAI(api_key="API_KEY")  # Replace with your real key

# -------------------------
# Language code -> name mapping
# -------------------------
LANGUAGES = {
    'en':'English','fr':'French','de':'German','hi':'Hindi','ko':'Korean',
    'gu':'Gujarati','ja':'Japanese','es':'Spanish','it':'Italian',
    'ru':'Russian','ar':'Arabic','tr':'Turkish','pt':'Portuguese',
    'zh-cn':'Chinese (Simplified)','zh-tw':'Chinese (Traditional)'
}

# -------------------------
# AI response function
# -------------------------
def generate_ai_response(user_input, lang_code):
    lang_name = LANGUAGES.get(lang_code, "the same language")
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are a helpful multilingual assistant. Always reply in {lang_name}."},
                {"role": "user", "content": user_input}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"(AI error: {e})"

# -------------------------
# Main chat loop
# -------------------------
print("Multilingual AI chatbot (type 'exit' to quit)")

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break

    # Detect language
    try:
        lang_code = detect(user_input)
    except:
        lang_code = "unknown"

    lang_name = LANGUAGES.get(lang_code, "Unknown")
    print(f"You wrote in {lang_name} ({lang_code}): {user_input}")

    # Generate AI reply
    response = generate_ai_response(user_input, lang_code)
    print(f"Bot: ({lang_name}): {response}\n")

    # Save conversation in MongoDB
    try:
        result = collection.insert_one({
            "user_input": user_input,
            "language_code": lang_code,
            "language_name": lang_name,
            "response": response,
            "timestamp": datetime.now(timezone.utc)
        })
        print("💾 Saved in MongoDB with ID:", result.inserted_id)
    except Exception as e:
        print("⚠️ Could not save to MongoDB:", e)
