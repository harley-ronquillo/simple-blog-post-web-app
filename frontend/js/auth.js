// DOM Elements
const loginBtn = document.getElementById('loginBtn');
const signupBtn = document.getElementById('signupBtn');
const genreSelection = document.getElementById('genreSelection');
const blogFeed = document.getElementById('blogFeed');

// API URL
const API_URL = 'http://localhost:5000';

// Get current page
const currentPage = window.location.pathname.split('/').pop() || 'index.html';

// Event Listeners
loginBtn.addEventListener('click', () => {
    loginForm.classList.remove('hidden');
    signupForm.classList.add('hidden');
    genreSelection.classList.add('hidden');
    blogFeed.classList.add('hidden');
});

signupBtn.addEventListener('click', () => {
    signupForm.classList.remove('hidden');
    loginForm.classList.add('hidden');
    genreSelection.classList.add('hidden');
    blogFeed.classList.add('hidden');
});

// Handle Login Page
if (currentPage === 'index.html') {
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('loginUsername').value;
            const password = document.getElementById('loginPassword').value;

            try {
                const response = await fetch(`${API_URL}/auth/login`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ username, password })
                });

                const data = await response.json();

                if (response.ok) {
                    localStorage.setItem('token', data.token);
                    localStorage.setItem('userId', data.user_id);
                    localStorage.setItem('username', username);
                    window.location.href = 'home.html';
                } else {
                    alert(data.message || 'Login failed');
                }
            } catch (error) {
                console.error('Login error:', error);
                alert('Login failed. Please try again.');
            }
        });
    }
}

// Handle Signup Page
if (currentPage === 'signup.html') {
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const username = document.getElementById('signupUsername').value;
            const email = document.getElementById('signupEmail').value;
            const password = document.getElementById('signupPassword').value;

            try {
                const response = await fetch(`${API_URL}/auth/signup`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ username, email, password })
                });

                const data = await response.json();

                if (response.ok) {
                    localStorage.setItem('token', data.token);
                    localStorage.setItem('userId', data.user_id);
                    localStorage.setItem('username', username);
                    window.location.href = 'home.html';
                } else {
                    alert(data.message || 'Signup failed');
                }
            } catch (error) {
                console.error('Signup error:', error);
                alert('Signup failed. Please try again.');
            }
        });
    }
}

// Helper Functions
function showGenreSelection() {
    loginForm.classList.add('hidden');
    signupForm.classList.add('hidden');
    genreSelection.classList.remove('hidden');
    blogFeed.classList.add('hidden');
}

function showBlogFeed() {
    loginForm.classList.add('hidden');
    signupForm.classList.add('hidden');
    genreSelection.classList.add('hidden');
    blogFeed.classList.remove('hidden');
}

// Check authentication status
function checkAuth() {
    const token = localStorage.getItem('token');
    if (token) {
        // If we're on login or signup page and we're already authenticated,
        // redirect to home page
        if (currentPage === 'index.html' || currentPage === 'signup.html') {
            window.location.href = 'home.html';
        }
    } else {
        // If we're on home page and we're not authenticated,
        // redirect to login page
        if (currentPage === 'home.html') {
            window.location.href = 'index.html';
        }
    }
}

// Initialize
checkAuth(); 