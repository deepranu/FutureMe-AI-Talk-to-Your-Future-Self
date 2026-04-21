# from flask import Flask, request, jsonify
# import openai
# import os
# from dotenv import load_dotenv
# from flask_cors import CORS

# load_dotenv()

# app = Flask(__name__)
# CORS(app)

# openai.api_key = os.getenv("OPENAI_API_KEY")

# @app.route("/chat", methods=["POST"])
# def chat():
#     user_input = request.json.get("message")

#     prompt = f"""
#     You are the future version of the user.
#     The user says: {user_input}

#     Respond like a wiser, more experienced version of them.
#     Give advice, reflection, and motivation.
#     """

#     response = openai.ChatCompletion.create(
#         model="gpt-4o-mini",
#         messages=[{"role": "user", "content": prompt}]
#     )

#     reply = response.choices[0].message.content

#     return jsonify({"response": reply})

# if __name__ == "__main__":
#     app.run(debug=True)


















from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import time

app = Flask(__name__)
CORS(app)

openai.api_key = "YOUR_OPENAI_API_KEY"

# 🧠 Chat memory
chat_history = []

# 🎯 System prompt (improved)
SYSTEM_PROMPT = {
    "role": "system",
    "content": """
    You are the user's future self (10 years ahead).

    Rules:
    - Be honest and practical
    - Avoid generic motivation
    - Give actionable advice
    - Mention consequences of decisions

    Format your response like:
    1. Reflection
    2. Advice
    3. Reality Check
    """
}

# ⚡ Retry logic (handles API failures)
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

    return "⚠️ API is busy. Please try again later."


# 🧹 Input preprocessing
def clean_input(text):
    return text.strip()


# 🧹 Output post-processing
def clean_output(text):
    return text.strip()


@app.route("/chat", methods=["POST"])
def chat():
    global chat_history

    data = request.get_json()
    user_input = data.get("message")

    if not user_input:
        return jsonify({"response": "Please enter a message"}), 400

    # 🧹 Clean input
    user_input = clean_input(user_input)

    # Add user message
    chat_history.append({"role": "user", "content": user_input})

    # Prepare messages
    messages = [SYSTEM_PROMPT] + chat_history

    start_time = time.time()

    # ⚡ Call API with retry
    reply = call_openai(messages)

    end_time = time.time()

    # 🧹 Clean output
    reply = clean_output(reply)

    # Save response
    chat_history.append({"role": "assistant", "content": reply})

    # 📊 Logging (for evaluation)
    print("User:", user_input)
    print("AI:", reply)
    print("Response Time:", round(end_time - start_time, 2), "sec")

    return jsonify({
        "response": reply,
        "response_time": round(end_time - start_time, 2)
    })


# 🔄 Reset chat
@app.route("/reset", methods=["POST"])
def reset_chat():
    global chat_history
    chat_history = []
    return jsonify({"message": "Chat reset successful"})


if __name__ == "__main__":
    app.run(debug=True)
