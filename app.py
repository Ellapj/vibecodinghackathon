import os
import datetime
import requests
from flask import Flask, render_template, request, jsonify, url_for

app = Flask(__name__)

# Hugging Face API configuration - Updated to a working model
API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
headers = {
    "Authorization": "Bearer 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"
}

# In-memory "database"
users = {}
next_user_id = 1

def generate_flashcards(text):
    """Generates flashcards from text using a different approach."""
    try:
        # Split text into sentences for basic question generation
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        flashcards = []
        
        for i, sentence in enumerate(sentences[:5]):  # Limit to 5 flashcards
            if len(sentence) > 10:  # Only process meaningful sentences
                # Create simple question-answer pairs
                words = sentence.split()
                if len(words) > 5:
                    # Create fill-in-the-blank style questions
                    key_word = words[len(words)//2]  # Pick a middle word
                    question = sentence.replace(key_word, "______")
                    answer = key_word
                    flashcards.append({
                        "question": f"Fill in the blank: {question}",
                        "answer": answer
                    })
                else:
                    # Create simple Q&A
                    flashcards.append({
                        "question": f"What is important about: {sentence[:50]}...?",
                        "answer": sentence
                    })
        
        # If no flashcards generated, create a fallback
        if not flashcards:
            flashcards = [{
                "question": "What did you study?",
                "answer": text[:100] + "..." if len(text) > 100 else text
            }]
            
        return flashcards
        
    except Exception as e:
        print(f"Flashcard generation error: {e}")
        # Return sample flashcards as fallback
        return [
            {
                "question": "Review your notes: What are the key concepts?",
                "answer": "Check your study material for important topics."
            }
        ]

@app.route("/")
def index():
    """Renders the main landing page."""
    return render_template('index.html')

@app.route("/signup", methods=["GET", "POST"])
def signup():
    """Handles user sign up."""
    if request.method == "POST":
        global next_user_id
        data = request.json
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        
        if not all([name, email, password]):
            return jsonify({"success": False, "error": "All fields are required."}), 400
        
        # Check if email already exists
        if email in [user["email"] for user in users.values()]:
            return jsonify({"success": False, "error": "Email already registered."}), 409
        
        user_id = next_user_id
        next_user_id += 1
        
        # Create user with proper structure
        users[user_id] = {
            "id": user_id,
            "name": name,
            "email": email,
            "password": password,
            "is_premium": False,
            "trial_start": datetime.date.today().isoformat(),
            "flashcards": []
        }
        
        print(f"User created: {users[user_id]}")  # Debug log
        return jsonify({"success": True, "user_id": user_id})
    
    return render_template('signup.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    """Handles user login."""
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
    """Renders the user dashboard."""
    user = users.get(user_id)
    if user:
        return render_template('dashboard.html', user=user, flashcards=user.get("flashcards", []))
    else:
        return "User not found", 404

@app.route("/generate_flashcards", methods=["POST"])
def generate_cards():
    """Generates and returns flashcards."""
    data = request.json
    notes = data.get('notes', '')
    
    if not notes.strip():
        return jsonify({"error": "No notes provided."}), 400
    
    flashcards = generate_flashcards(notes)
    return jsonify(flashcards)

@app.route("/save_flashcards", methods=["POST"])
def save_flashcards():
    """Saves generated flashcards to the user's profile."""
    data = request.json
    user_id = data.get("user_id")
    cards_data = data.get("flashcards")
    
    print(f"Saving flashcards - User ID: {user_id}, Cards: {len(cards_data) if cards_data else 0}")
    
    if not user_id or not cards_data:
        return jsonify({"success": False, "error": "Missing user ID or flashcards data."}), 400
    
    # Ensure user_id is an integer
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        return jsonify({"success": False, "error": "Invalid user ID format."}), 400
    
    user = users.get(user_id)
    if user:
        # Initialize flashcards list if it doesn't exist
        if "flashcards" not in user:
            user["flashcards"] = []
        
        # Add new flashcards to existing ones (don't overwrite)
        user["flashcards"].extend(cards_data)
        
        print(f"Successfully saved! User {user_id} now has {len(user['flashcards'])} total flashcards")
        print(f"Current users database: {list(users.keys())}")
        
        return jsonify({"success": True, "message": "Flashcards saved successfully!"})
    else:
        print(f"User {user_id} not found in database. Available users: {list(users.keys())}")
        return jsonify({"success": False, "error": "User not found."}), 404

@app.route("/get_flashcards/<int:user_id>", methods=["GET"])
def get_flashcards(user_id):
    """Retrieves saved flashcards for a user."""
    user = users.get(user_id)
    if user:
        flashcards = user.get("flashcards", [])
        print(f"Retrieved {len(flashcards)} flashcards for user {user_id}")  # Debug log
        return jsonify(flashcards)
    else:
        return jsonify([]), 404

@app.route("/payment/<int:user_id>")
def payment_page(user_id):
    """Renders the payment page."""
    user = users.get(user_id)
    if user:
        return render_template('payment.html', user_id=user_id, user=user)
    return "User not found", 404

@app.route("/initiate_payment", methods=["POST"])
def initiate_payment():
    """Handles payment completion."""
    user_id = request.form.get("user_id")
    if not user_id:
        return "User ID missing", 400
    
    try:
        user_id = int(user_id)
        user = users.get(user_id)
        if user:
            user["is_premium"] = True
            print(f"User {user_id} upgraded to premium")  # Debug log
            return jsonify({"success": True, "message": "Payment successful!"})
        return jsonify({"success": False, "error": "User not found"}), 404
    except ValueError:
        return "Invalid user ID", 400

@app.route("/payment_success/<int:user_id>")
def payment_success(user_id):
    """Handles successful payment callback."""
    user = users.get(user_id)
    if user:
        user["is_premium"] = True
        return f"Payment successful! <a href='/dashboard/{user_id}'>Go to Dashboard</a>"
    return "User not found", 404

if __name__ == '__main__':
    app.run(debug=True)