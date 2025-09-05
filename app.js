// Global variables for user info
window.currentUserId = null;
window.currentUserEmail = null;
window.currentUserName = null;

// ------------------- UTILITY FUNCTIONS -------------------
function getCurrentUserIdFromURL() {
  const parts = window.location.pathname.split('/');
  return parts[parts.length - 1];
}

function setCurrentUser(userId, email, name) {
  window.currentUserId = parseInt(userId);
  window.currentUserEmail = email;
  window.currentUserName = name;
}

// ------------------- FLASHCARD GENERATION -------------------
document.getElementById('generate-btn')?.addEventListener('click', () => {
  const notes = document.getElementById('study-notes').value;
  const flashcardContainer = document.getElementById('flashcard-container');

  if (!notes.trim()) {
    alert('Please enter some notes to generate flashcards.');
    return;
  }

  if (!flashcardContainer) {
    console.error('Flashcard container element not found.');
    return;
  }

  // Show loading state
  flashcardContainer.innerHTML = '<p>Generating flashcards...</p>';

  fetch('/generate_flashcards', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ notes })
  })
  .then(res => res.json())
  .then(data => {
    flashcardContainer.innerHTML = '';

    if (!data || data.length === 0) {
      flashcardContainer.innerHTML = '<p>No flashcards generated. Try again with different notes!</p>';
      return;
    }

    data.forEach(card => {
      const flashcard = document.createElement('div');
      flashcard.className = 'flashcard';
      flashcard.innerHTML = `
        <div class="flashcard-inner">
          <div class="flashcard-front"><p>${card.question}</p></div>
          <div class="flashcard-back"><p>${card.answer}</p></div>
        </div>
      `;
      flashcard.addEventListener('click', () => flashcard.classList.toggle('flipped'));
      flashcardContainer.appendChild(flashcard);
    });

    // Save flashcards if user is logged in
    const userId = window.currentUserId || getCurrentUserIdFromURL();
    if (userId && !isNaN(userId)) {
      fetch('/save_flashcards', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: parseInt(userId), flashcards: data })
      })
      .then(res => res.json())
      .then(resp => {
        if (resp.success) {
          console.log('Flashcards saved successfully!');
        } else {
          console.error('Save error:', resp.error);
        }
      })
      .catch(err => console.error('Save request error:', err));
    }
  })
  .catch(err => {
    console.error('Generation error:', err);
    flashcardContainer.innerHTML = '<p>Error generating flashcards. Please try again.</p>';
  });
});

// ------------------- LOAD SAVED FLASHCARDS -------------------
function loadSavedFlashcards(userId) {
  const flashcardContainer = document.getElementById('flashcard-container');

  if (!flashcardContainer || !userId) {
    console.error('Flashcard container element or User ID not found.');
    return;
  }

  fetch(`/get_flashcards/${userId}`)
    .then(res => res.json())
    .then(data => {
      flashcardContainer.innerHTML = '';

      if (!data || data.length === 0) {
        flashcardContainer.innerHTML = '<p>No saved flashcards yet. Generate some from your notes!</p>';
        return;
      }

      data.forEach((card, index) => {
        const flashcard = document.createElement('div');
        flashcard.className = 'flashcard';
        flashcard.innerHTML = `
          <div class="flashcard-inner">
            <div class="flashcard-front"><p>${card.question}</p></div>
            <div class="flashcard-back"><p>${card.answer}</p></div>
          </div>
        `;
        
        // Better click handling for saved flashcards too
        flashcard.addEventListener('click', function(e) {
          e.stopPropagation();
          console.log(`Clicked saved flashcard ${index + 1}`);
          this.classList.toggle('flipped');
        });
        
        flashcardContainer.appendChild(flashcard);
      });
    })
    .catch(err => {
      console.error('Load error:', err);
      flashcardContainer.innerHTML = '<p>Error loading flashcards.</p>';
    });
}

// ------------------- DASHBOARD AUTOLOAD -------------------
if (window.location.pathname.includes('dashboard')) {
  const userId = getCurrentUserIdFromURL();
  if (userId && !isNaN(userId)) {
    window.currentUserId = parseInt(userId);
    loadSavedFlashcards(userId);
    
    // Try to get user info for payment (this is a workaround since we don't have session management)
    // In a real app, you'd get this from localStorage or session
    const userInfo = localStorage.getItem(`user_${userId}`);
    if (userInfo) {
      const parsed = JSON.parse(userInfo);
      setCurrentUser(userId, parsed.email, parsed.name);
    }
  } else {
    console.error('Invalid user ID in URL.');
  }
}

// ------------------- LOGIN FUNCTIONALITY -------------------
const loginForm = document.getElementById('loginForm');
loginForm?.addEventListener('submit', function(e) {
  e.preventDefault();
  const email = e.target.email.value;
  const password = e.target.password.value;
  
  const data = { email, password };

  fetch('/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  .then(res => res.json())
  .then(resp => {
    if (resp.success && resp.user_id) {
      // Store user info for later use
      localStorage.setItem(`user_${resp.user_id}`, JSON.stringify({
        email: email,
        name: email.split('@')[0] // Use email prefix as name fallback
      }));
      
      window.location.href = `/dashboard/${resp.user_id}`;
    } else {
      alert(resp.error || 'Login failed');
    }
  })
  .catch(err => {
    console.error('Login error:', err);
    alert('Login failed. Please try again.');
  });
});

// ------------------- SIGNUP FUNCTIONALITY -------------------
const signupForm = document.getElementById('signupForm');
signupForm?.addEventListener('submit', function(e) {
  e.preventDefault();
  const name = e.target.username.value;
  const email = e.target.email.value;
  const password = e.target.password.value;
  
  const data = { name, email, password };

  fetch('/signup', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  })
  .then(res => res.json())
  .then(resp => {
    if (resp.success && resp.user_id) {
      // Store user info for later use
      localStorage.setItem(`user_${resp.user_id}`, JSON.stringify({
        email: email,
        name: name
      }));
      
      setCurrentUser(resp.user_id, email, name);
      alert('Signup successful! Welcome to AI Study Buddy!');
      // Fixed: Go directly to dashboard instead of login
      window.location.href = `/dashboard/${resp.user_id}`;
    } else {
      alert(resp.error || 'Signup failed');
    }
  })
  .catch(err => {
    console.error('Signup error:', err);
    alert('Signup failed. Please try again.');
  });
});

// ------------------- FLUTTERWAVE PAYMENT -------------------
document.getElementById('flutterwave-btn')?.addEventListener('click', function(e) {
  e.preventDefault();
  payWithFlutterwave();
});

function payWithFlutterwave() {
  const userId = window.currentUserId || getCurrentUserIdFromURL();
  
  if (!userId) {
    alert("User ID missing. Please refresh the page and try again.");
    return;
  }

  // Get user info from localStorage if not in memory
  let userEmail = window.currentUserEmail;
  let userName = window.currentUserName;
  
  if (!userEmail || !userName) {
    const userInfo = localStorage.getItem(`user_${userId}`);
    if (userInfo) {
      const parsed = JSON.parse(userInfo);
      userEmail = parsed.email;
      userName = parsed.name;
    } else {
      // Fallback: prompt user for email
      userEmail = prompt("Please enter your email for payment:");
      userName = prompt("Please enter your name for payment:");
      if (!userEmail || !userName) {
        alert("Email and name are required for payment.");
        return;
      }
    }
  }

  // Initialize Flutterwave payment
  if (typeof FlutterwaveCheckout === 'undefined') {
    alert("Payment system not loaded. Please refresh the page and try again.");
    return;
  }

  FlutterwaveCheckout({
    public_key: "FLWPUBK_TEST-18534f6c3ccce11f5dc3a509c36f4314-X", // Your actual public key
    tx_ref: "aibuddy_" + Date.now(),
    amount: 2000,
    currency: "NGN",
    payment_options: "card,banktransfer,ussd",
    customer: {
      email: userEmail,
      name: userName,
      phone_number: "08012345678" // Add a default phone number
    },
    callback: function (data) {
      console.log("Payment callback data:", data);
      
      if (data.status === "successful") {
        alert("Payment successful! Upgrading your account...");
        
        // Update user to premium
        fetch('/initiate_payment', {
          method: 'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          body: `user_id=${userId}`
        })
        .then(res => res.json())
        .then(resp => {
          if (resp.success) {
            window.location.href = `/dashboard/${userId}`;
          } else {
            alert("Payment processed but account upgrade failed. Please contact support.");
          }
        })
        .catch(err => {
          console.error('Payment processing error:', err);
          alert("Payment successful but there was an error upgrading your account. Please contact support.");
        });
      } else {
        alert("Payment was not successful. Please try again.");
      }
    },
    onclose: function () {
      console.log("Payment modal closed");
    },
    customizations: {
      title: "AI Study Buddy Premium",
      description: "Unlimited Flashcard Generation",
      logo: ""
    }
  });
}