// DOM Elements
const genreGrid = document.querySelector('.genre-grid');
const submitGenresBtn = document.getElementById('submitGenres');

// State
let selectedGenres = new Set();
const MIN_GENRES = 3;

// Fetch Genres
async function fetchGenres() {
    try {
        const response = await fetch(`${API_URL}/genres`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        const genres = await response.json();
        displayGenres(genres);
    } catch (error) {
        console.error('Error fetching genres:', error);
        alert('Failed to load genres. Please refresh the page.');
    }
}

// Display Genres
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

// Toggle Genre Selection
function toggleGenre(genreElement) {
    const genreId = genreElement.dataset.id;
    
    if (selectedGenres.has(genreId)) {
        selectedGenres.delete(genreId);
        genreElement.classList.remove('selected');
    } else {
        selectedGenres.add(genreId);
        genreElement.classList.add('selected');
    }

    // Enable/disable submit button based on selection count
    submitGenresBtn.disabled = selectedGenres.size < MIN_GENRES;
}

// Submit Genre Selections
submitGenresBtn.addEventListener('click', async () => {
    try {
        const response = await fetch(`${API_URL}/users/genres`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({
                genre_ids: Array.from(selectedGenres)
            })
        });

        if (response.ok) {
            showBlogFeed();
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
if (genreSelection) {
    fetchGenres();
} 