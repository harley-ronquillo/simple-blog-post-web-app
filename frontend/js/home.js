// DOM Elements
const username = document.getElementById('username');
const userGenres = document.getElementById('userGenres');
const newPostBtn = document.getElementById('newPostBtn');
const postModal = document.getElementById('postModal');
const addGenreBtn = document.getElementById('addGenreBtn');
const addGenreModal = document.getElementById('addGenreModal');
const newGenreName = document.getElementById('newGenreName');
const submitGenre = document.getElementById('submitGenre');
const closeButtons = document.querySelectorAll('.close-btn');
const logoutBtn = document.getElementById('logoutBtn');

// Check authentication and genre selection status
async function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'index.html';
        return;
    }

    try {
        const response = await fetch(`${API_URL}/genres/status`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        const data = await response.json();

        if (!data.has_selected_genres) {
            window.location.href = 'genre-selection.html';
        }
    } catch (error) {
        console.error('Error checking genre status:', error);
    }
}

// Set username
username.textContent = localStorage.getItem('username');

// Fetch and display user's genres
async function fetchUserGenres() {
    try {
        const response = await fetch(`${API_URL}/genres/user`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        const genres = await response.json();
        displayUserGenres(genres);
    } catch (error) {
        console.error('Error fetching user genres:', error);
    }
}

// Display user's genres
function displayUserGenres(genres) {
    userGenres.innerHTML = genres.map(genre => `
        <div class="genre-item" data-id="${genre.id}">
            ${genre.name}
        </div>
    `).join('');
    
    // Add click handlers
    document.querySelectorAll('.genre-item').forEach(item => {
        item.addEventListener('click', () => {
            document.querySelectorAll('.genre-item').forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            // Filter posts by genre
            filterPostsByGenre(item.dataset.id);
        });
    });
}

// Add new genre
async function addNewGenre(genreName) {
    try {
        const response = await fetch(`${API_URL}/genres/add`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({ name: genreName })
        });

        if (response.ok) {
            const data = await response.json();
            fetchUserGenres(); // Refresh genres list
            addGenreModal.classList.add('hidden');
            newGenreName.value = '';
        } else {
            const data = await response.json();
            alert(data.message || 'Failed to add genre');
        }
    } catch (error) {
        console.error('Error adding genre:', error);
        alert('Failed to add genre. Please try again.');
    }
}

// Filter posts by genre
function filterPostsByGenre(genreId) {
    const posts = document.querySelectorAll('.post');
    posts.forEach(post => {
        if (genreId === 'all' || post.dataset.genreId === genreId) {
            post.style.display = 'block';
        } else {
            post.style.display = 'none';
        }
    });
}

// Modal handlers
newPostBtn.addEventListener('click', () => {
    postModal.classList.remove('hidden');
});

addGenreBtn.addEventListener('click', () => {
    addGenreModal.classList.remove('hidden');
});

submitGenre.addEventListener('click', () => {
    const genreName = newGenreName.value.trim();
    if (genreName) {
        addNewGenre(genreName);
    } else {
        alert('Please enter a genre name');
    }
});

// Close modals when clicking outside or on close button
closeButtons.forEach(button => {
    button.addEventListener('click', () => {
        button.closest('.modal').classList.add('hidden');
    });
});

[postModal, addGenreModal].forEach(modal => {
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.add('hidden');
        }
    });
});

// Logout handler
logoutBtn.addEventListener('click', () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userId');
    localStorage.removeItem('username');
    window.location.href = 'index.html';
});

// Initialize
checkAuth();
fetchUserGenres(); 