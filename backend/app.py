from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import time
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

openai.api_key = os.getenv("OPENAI_API_KEY")

chat_history = []
MAX_HISTORY = 6

SYSTEM_PROMPT = {
    "role": "system",
    "content": """
    You are the user's future self (10 years ahead).

    Be honest, practical, and realistic.

    Avoid generic motivation.

    Format:
    1. Reflection
    2. Advice
    3. Reality Check
    """
}

def call_openai(messages, retries=2):
    for attempt in range(retries):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7,
                timeout=10
            )
            return response["choices"][0]["message"]["content"]
        except Exception as e:
            print("Retry:", e)
            time.sleep(1)

    return "⚠️ Error: Try again later"


def clean_input(text):
    return text.strip()[:500]


@app.route("/chat", methods=["POST"])
def chat():
    global chat_history

    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"response": "Invalid input"}), 400

    user_input = clean_input(data["message"])

    chat_history.append({"role": "user", "content": user_input})

    # Limit memory
    chat_history = chat_history[-MAX_HISTORY:]

    messages = [SYSTEM_PROMPT] + chat_history

    start = time.time()

    reply = call_openai(messages)

    end = time.time()

    chat_history.append({"role": "assistant", "content": reply})

    return jsonify({
        "response": reply,
        "response_time": round(end - start, 2)
    })


@app.route("/reset", methods=["POST"])
def reset_chat():
    global chat_history
    chat_history = []
    return jsonify({"message": "Reset done"})


if __name__ == "__main__":
    app.run(debug=True)
