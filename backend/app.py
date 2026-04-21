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

MAX_HISTORY = 6  # limit memory (important for latency)

SYSTEM_PROMPT = {
    "role": "system",
    "content": """
    You are the user's future self (10 years ahead).

    Be:
    - Honest
    - Practical
    - Emotionally intelligent

    Avoid:
    - Generic motivation
    - Overly positive fluff

    Respond in format:
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
            print(f"Retry {attempt+1} failed:", e)
            time.sleep(1)

    return "⚠️ I'm having trouble responding right now. Please try again."


def clean_input(text):
    return text.strip()[:500]  # limit length (guardrail)


def clean_output(text):
    return text.strip()


@app.route("/chat", methods=["POST"])
def chat():
    global chat_history

    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"response": "Invalid input"}), 400

    user_input = clean_input(data["message"])

    if len(user_input) == 0:
        return jsonify({"response": "Please enter a valid message"}), 400

    chat_history.append({"role": "user", "content": user_input})

    # 🔥 limit history (performance fix)
    chat_history = chat_history[-MAX_HISTORY:]

    messages = [SYSTEM_PROMPT] + chat_history

    start_time = time.time()

    reply = call_openai(messages)

    end_time = time.time()

    reply = clean_output(reply)

    chat_history.append({"role": "assistant", "content": reply})

    response_time = round(end_time - start_time, 2)

    # 📊 Logging (for evaluation)
    print("=" * 40)
    print("User:", user_input)
    print("AI:", reply)
    print("Response Time:", response_time, "sec")

    return jsonify({
        "response": reply,
        "response_time": response_time
    })


@app.route("/reset", methods=["POST"])
def reset_chat():
    global chat_history
    chat_history = []
    return jsonify({"message": "Chat reset"})


if __name__ == "__main__":
    app.run(debug=True)
