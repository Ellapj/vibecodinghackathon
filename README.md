# AI Study Buddy

AI Study Buddy is a web application designed to help students generate, save, and study flashcards from their notes. It features user authentication, a premium plan with advanced features, and mood tracking to monitor study trends.

---

## Table of Contents

* [Features](#features)
* [Demo](#demo)
* [Tech Stack](#tech-stack)
* [Installation](#installation)
* [Usage](#usage)
* [Project Structure](#project-structure)
* [Database Setup](#database-setup)
* [Contributing](#contributing)
* [License](#license)

---

## Features

* **Flashcard Generation**: Paste your study notes to automatically generate flashcards.
* **Flashcard Saving**: Save flashcards for later review.
* **Mood Trend Tracker**: Track study mood and performance trends.
* **User Authentication**: Signup and login securely.
* **Premium Plan**: Upgrade to unlock unlimited flashcards and advanced features via Flutterwave payment integration.
* **Responsive Design**: Works on desktop, tablet, and mobile devices.

---

## Demo

You can run the app locally:

* Home Page: `http://127.0.0.1:5000/`
* Login Page: `http://127.0.0.1:5000/login-page`
* Signup Page: `http://127.0.0.1:5000/signup-page`
* Dashboard: `http://127.0.0.1:5000/dashboard/<user_id>`

---

## Tech Stack

* **Frontend**: HTML, CSS, JavaScript
* **Backend**: Python, Flask
* **Database**: MySQL
* **APIs**: Hugging Face (for flashcard generation), Flutterwave (payment integration)

---

## Installation

1. **Clone the repository**

```bash
git clone <your-repo-url>
cd ai-study-buddy
```

2. **Create a virtual environment and activate it**

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Mac/Linux
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up your MySQL database**
   Create a database called `study_buddy` and tables `users` and `flashcards` (see [Database Setup](#database-setup)).

5. **Run the app**

```bash
python app.py
```

6. **Open in browser**
   Go to `http://127.0.0.1:5000/`

---

## Usage

1. **Signup**: Create a new account via the Signup page.
2. **Login**: Log in with your credentials.
3. **Generate Flashcards**: Paste notes and click "Generate Flashcards".
4. **View Flashcards**: Flashcards appear below the notes section. Click a flashcard to flip it.
5. **Premium Upgrade**: Upgrade to unlock unlimited flashcards via Flutterwave.

---

## Project Structure

```
ai-study-buddy/
│
├── static/
│   ├── styles.css        # CSS styling
│   └── app.js            # JavaScript functionality
│
├── templates/
│   ├── index.html        # Home page with notes & Mood Trend
│   ├── login.html        # Login page
│   ├── signup.html       # Signup page
│   ├── dashboard.html    # Dashboard with saved flashcards
│   └── payment.html      # Premium upgrade page
│
├── app.py                # Flask application
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

---

## Database Setup

**MySQL Tables**:

```sql
CREATE DATABASE study_buddy;

USE study_buddy;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password_hash VARCHAR(255),
    trial_start DATETIME,
    is_premium BOOLEAN DEFAULT FALSE
);

CREATE TABLE flashcards (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    question TEXT,
    answer TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/feature-name`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/feature-name`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

