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
import os

app = Flask(__name__)
CORS(app)

# 🔑 Add your API key here or use environment variable
openai.api_key = "YOUR_OPENAI_API_KEY"

# 🧠 Global chat memory (basic version)
chat_history = []

# 🎯 System prompt (your app's personality)
SYSTEM_PROMPT = {
    "role": "system",
    "content": """
    You are the user's future self from 10 years ahead.

    You are:
    - Honest, not sugar-coating
    - Practical, not vague
    - Emotionally intelligent

    You:
    - Reflect on user's situation
    - Give actionable advice
    - Mention possible consequences
    - Speak like you truly lived their life

    Avoid generic motivation.
    """
}

@app.route("/chat", methods=["POST"])
def chat():
    global chat_history

    data = request.get_json()
    user_input = data.get("message")

    if not user_input:
        return jsonify({"response": "No input provided"}), 400

    # Add user message to history
    chat_history.append({"role": "user", "content": user_input})

    try:
        # Combine system prompt + chat history
        messages = [SYSTEM_PROMPT] + chat_history

        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7
        )

        reply = response["choices"][0]["message"]["content"]

        # Save AI response to history
        chat_history.append({"role": "assistant", "content": reply})

        return jsonify({"response": reply})

    except Exception as e:
        print("Error:", e)
        return jsonify({
            "response": "⚠️ Something went wrong. Please try again."
        }), 500


# 🔄 Optional: Reset chat (useful feature)
@app.route("/reset", methods=["POST"])
def reset_chat():
    global chat_history
    chat_history = []
    return jsonify({"message": "Chat reset successful"})


if __name__ == "__main__":
    app.run(debug=True)
