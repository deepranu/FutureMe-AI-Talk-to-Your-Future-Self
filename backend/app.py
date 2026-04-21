from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai
import time

app = Flask(__name__)
CORS(app)

# 🔑 Add your OpenAI API key
openai.api_key = "YOUR_OPENAI_API_KEY"

# 🧠 Memory
chat_history = []

# 🎯 Future Self Prompt
SYSTEM_PROMPT = {
    "role": "system",
    "content": """
    You are the user's future self (10 years ahead).

    Rules:
    - Be honest and practical
    - Avoid generic motivation
    - Give actionable advice
    - Mention consequences

    Format:
    1. Reflection
    2. Advice
    3. Reality Check
    """
}

# ⚡ API Retry Logic
def call_openai(messages, retries=2):
    for attempt in range(retries):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.7
            )
            return response["choices"][0]["message"]["content"]

        except Exception as e:
            print(f"Retry {attempt+1} failed:", e)
            time.sleep(1)

    return "⚠️ API busy. Try again later."


# 🧹 Input Clean
def clean_input(text):
    return text.strip()


# 🧹 Output Clean
def clean_output(text):
    return text.strip()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    global chat_history

    data = request.get_json()
    user_input = data.get("message")

    if not user_input:
        return jsonify({"response": "Please enter a message"}), 400

    user_input = clean_input(user_input)

    chat_history.append({"role": "user", "content": user_input})

    messages = [SYSTEM_PROMPT] + chat_history

    start_time = time.time()

    reply = call_openai(messages)

    end_time = time.time()

    reply = clean_output(reply)

    chat_history.append({"role": "assistant", "content": reply})

    print("User:", user_input)
    print("AI:", reply)
    print("Time:", round(end_time - start_time, 2), "sec")

    return jsonify({
        "response": reply,
        "response_time": round(end_time - start_time, 2)
    })


@app.route("/reset", methods=["POST"])
def reset_chat():
    global chat_history
    chat_history = []
    return jsonify({"message": "Chat reset"})


if __name__ == "__main__":
    app.run(debug=True)
