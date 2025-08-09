// Check authentication
const token = localStorage.getItem('token');
if (!token) {
    window.location.href = 'index.html';
}

// DOM Elements
const genreGrid = document.getElementById('genreGrid');
const selectedCount = document.getElementById('selectedCount');
const continueBtn = document.getElementById('continueBtn');

// State
const selectedGenres = new Set();
const MIN_GENRES = 3;

// Fetch genres
async function fetchGenres() {
    try {
        const response = await fetch(`${API_URL}/genres`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        const genres = await response.json();
        displayGenres(genres);
    } catch (error) {
        console.error('Error fetching genres:', error);
        alert('Failed to load genres. Please refresh the page.');
    }
}

// Display genres
function displayGenres(genres) {
    genreGrid.innerHTML = genres.map(genre => `
        <div class="genre-item" data-id="${genre.id}">
            ${genre.name}
        </div>
    `).join('');

    // Add click handlers
    genreGrid.querySelectorAll('.genre-item').forEach(item => {
        item.addEventListener('click', () => toggleGenre(item));
    });
}

// Toggle genre selection
function toggleGenre(genreElement) {
    const genreId = genreElement.dataset.id;
    
    if (selectedGenres.has(genreId)) {
        selectedGenres.delete(genreId);
        genreElement.classList.remove('selected');
    } else {
        selectedGenres.add(genreId);
        genreElement.classList.add('selected');
    }

    // Update count and button state
    selectedCount.textContent = selectedGenres.size;
    continueBtn.disabled = selectedGenres.size < MIN_GENRES;
}

// Submit genre selections
continueBtn.addEventListener('click', async () => {
    try {
        const response = await fetch(`${API_URL}/genres/user`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                genre_ids: Array.from(selectedGenres)
            })
        });

        if (response.ok) {
            window.location.href = 'home.html';
        } else {
            const data = await response.json();
            alert(data.message || 'Failed to save genre preferences');
        }
    } catch (error) {
        console.error('Error saving genres:', error);
        alert('Failed to save genre preferences. Please try again.');
    }
});

// Initialize
fetchGenres(); 