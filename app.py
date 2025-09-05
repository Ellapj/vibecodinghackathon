from dotenv import load_dotenv
import os
import datetime
import requests
from flask import Flask, render_template, request, jsonify, url_for

# Load environment variables
load_dotenv()
API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Hugging Face API configuration
API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
headers = {
    "Authorization": f"Bearer {API_KEY}"
}

app = Flask(__name__)

# In-memory "database"
users = {}
next_user_id = 1

def generate_flashcards(text):
    try:
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        flashcards = []

        for i, sentence in enumerate(sentences[:5]):
            if len(sentence) > 10:
                words = sentence.split()
                if len(words) > 5:
                    key_word = words[len(words)//2]
                    question = sentence.replace(key_word, "______")
                    answer = key_word
                    flashcards.append({
                        "question": f"Fill in the blank: {question}",
                        "answer": answer
                    })
                else:
                    flashcards.append({
                        "question": f"What is important about: {sentence[:50]}...?",
                        "answer": sentence
                    })

        if not flashcards:
            flashcards = [{
                "question": "What did you study?",
                "answer": text[:100] + "..." if len(text) > 100 else text
            }]

        return flashcards

    except Exception as e:
        print(f"Flashcard generation error: {e}")
        return [{
            "question": "Review your notes: What are the key concepts?",
            "answer": "Check your study material for important topics."
        }]

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/signup", methods=["GET", "POST"])
def signup():
    global next_user_id
    if request.method == "POST":
        data = request.json
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        if not all([name, email, password]):
            return jsonify({"success": False, "error": "All fields are required."}), 400

        if email in [user["email"] for user in users.values()]:
            return jsonify({"success": False, "error": "Email already registered."}), 409

        user_id = next_user_id
        next_user_id += 1

        users[user_id] = {
            "id": user_id,
            "name": name,
            "email": email,
            "password": password,
            "is_premium": False,
            "trial_start": datetime.date.today().isoformat(),
            "flashcards": []
        }

        print(f"User created: {users[user_id]}")
        return jsonify({"success": True, "user_id": user_id})

    return render_template('signup.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.json
        email = data.get("email")
        password = data.get("password")

        user = next((u for u in users.values() if u["email"] == email and u["password"] == password), None)
        if user:
            return jsonify({"success": True, "user_id": user["id"]})
        else:
            return jsonify({"success": False, "error": "Invalid email or password."}), 401

    return render_template('login.html')

@app.route("/dashboard/<int:user_id>")
def dashboard(user_id):
    user = users.get(user_id)
    if user:
        return render_template('dashboard.html', user=user, flashcards=user.get("flashcards", []))
    else:
        return "User not found", 404

@app.route("/generate_flashcards", methods=["POST"])
def generate_cards():
    data = request.json
    notes = data.get('notes', '')

    if not notes.strip():
        return jsonify({"error": "No notes provided."}), 400

    flashcards = generate_flashcards(notes)
    return jsonify(flashcards)

@app.route("/save_flashcards", methods=["POST"])
def save_flashcards():
    data = request.json
    user_id = data.get("user_id")
    cards_data = data.get("flashcards")

    print(f"Saving flashcards - User ID: {user_id}, Cards: {len(cards_data) if cards_data else 0}")

    if not user_id or not cards_data:
        return jsonify({"success": False, "error": "Missing user ID or flashcards data."}), 400

    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Invalid user ID format."}), 400

    user = users.get(user_id)
    if user:
        user.setdefault("flashcards", []).extend(cards_data)
        print(f"Successfully saved! User {user_id} now has {len(user['flashcards'])} total flashcards")
        return jsonify({"success": True, "message": "Flashcards saved successfully!"})
    else:
        return jsonify({"success": False, "error": "User not found."}), 404

@app.route("/get_flashcards/<int:user_id>", methods=["GET"])
def get_flashcards(user_id):
    user = users.get(user_id)
    if user:
        flashcards = user.get("flashcards", [])
        print(f"Retrieved {len(flashcards)} flashcards for user {user_id}")
        return jsonify(flashcards)
    else:
        return jsonify([]), 404

@app.route("/payment/<int:user_id>")
def payment_page(user_id):
    user = users.get(user_id)
    if user:
        return render_template('payment.html', user_id=user_id, user=user)
    return "User not found", 404

@app.route("/initiate_payment", methods=["POST"])
def initiate_payment():
    user_id = request.form.get("user_id")
    if not user_id:
        return "User ID missing", 400

    try:
        user_id = int(user_id)
        user = users.get(user_id)
        if user:
            user["is_premium"] = True
            print(f"User {user_id} upgraded to premium")
            return jsonify({"success": True, "message": "Payment successful!"})
        return jsonify({"success": False, "error": "User not found"}), 404
    except ValueError:
        return "Invalid user ID", 400

@app.route("/payment_success/<int:user_id>")
def payment_success(user_id):
    user = users.get(user_id)
    if user:
        user["is_premium"] = True
        return f"Payment successful! <a href='/dashboard/{user_id}'>Go to Dashboard</a>"
    return "User not found", 404

if __name__ == '__main__':
    app.run(debug=True)