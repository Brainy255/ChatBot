import os
from flask import Flask, request, jsonify, render_template
from groq import Groq
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

base_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=base_dir, static_folder=base_dir, static_url_path='')




# API Key should ideally be in env vars, but I'll stick to the provided one or use a placeholder if it's invalid.
# For this task, I'll use the one provided in the original file.
GROQ_API_KEY = "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"

try:
    client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    logger.error(f"Failed to initialize Groq client: {e}")
    client = None

KNOWLEDGE_FILE = os.path.join(os.path.dirname(__file__), "knowledge.txt")

def load_knowledge():
    try:
        if os.path.exists(KNOWLEDGE_FILE):
            with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
                return f.read()
    except Exception as e:
        logger.error(f"Error loading knowledge base: {e}")
    return "No knowledge base available."

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    if not client:
        return jsonify({"reply": "Error: Chat service is currently unavailable."}), 500

    data = request.json
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "Please enter a message."}), 400

    knowledge = load_knowledge()

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a strictly specialized expert assistant in Cloud-based AI/MI services and Quantum Computing. "
                        "STRICTLY ONLY answer questions related to these specific topics. "
                        "If a user asks about anything else (e.g., accounting, sports, cooking, general chitchat), "
                        "politely decline and remind them that you are only here to discuss Cloud AI and Quantum Computing. "
                        "Ensure your answers reflect the provided knowledge base where applicable.\n\n"
                        f"Knowledge Base:\n{knowledge}"
                    )
                },
                {"role": "user", "content": user_message}
            ],
            temperature=0.3, # Lower temperature for more consistent, focused answers
            max_tokens=1024,
        )

        bot_reply = completion.choices[0].message.content
        return jsonify({"reply": bot_reply})

    except Exception as e:
        logger.error(f"Error during API call: {e}")
        return jsonify({"reply": "I'm sorry, I encountered an error while processing your request."}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)