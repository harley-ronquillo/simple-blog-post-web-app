import { API_URL } from './config.js';
// DOM Elements
const postsContainer = document.getElementById('posts');
const newPostTextarea = document.getElementById('newPost');
const postGenreSelect = document.getElementById('postGenre');
const submitPostBtn = document.getElementById('submitPost');

// Fetch posts
async function fetchPosts() {
    try {
        const response = await fetch(`${API_URL}/posts`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        const posts = await response.json();
        displayPosts(posts);
    } catch (error) {
        console.error('Error fetching posts:', error);
    }
}

// Display posts
function displayPosts(posts) {
    postsContainer.innerHTML = posts.map(post => `
        <div class="post" data-id="${post.id}" data-genre-id="${post.genre_id}">
            <div class="post-header">
                <div class="post-meta">
                    <span class="post-genre">${post.genre_name}</span>
                    <span class="post-date">${new Date(post.created_at).toLocaleDateString()}</span>
                </div>
            </div>
            <div class="post-content">${post.post_text}</div>
            <div class="post-actions">
                <button onclick="votePost('${post.id}', 'up')" class="vote-btn">
                    <i class="fas fa-thumbs-up"></i> ${post.up_vote_count}
                </button>
                <button onclick="votePost('${post.id}', 'down')" class="vote-btn">
                    <i class="fas fa-thumbs-down"></i> ${post.down_vote_count}
                </button>
                <button onclick="sharePost('${post.id}')" class="share-btn">
                    <i class="fas fa-share"></i> ${post.share_count}
                </button>
            </div>
        </div>
    `).join('');
}

// Create new post
submitPostBtn.addEventListener('click', async () => {
    const postText = newPostTextarea.value.trim();
    const genreId = postGenreSelect.value;

    if (!postText) {
        alert('Please write something in your post');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/posts`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({
                post_text: postText,
                genre_id: genreId
            })
        });

        if (response.ok) {
            // Clear form and close modal
            newPostTextarea.value = '';
            document.getElementById('postModal').classList.add('hidden');
            // Refresh posts
            fetchPosts();
        } else {
            const data = await response.json();
            alert(data.message || 'Failed to create post');
        }
    } catch (error) {
        console.error('Error creating post:', error);
        alert('Failed to create post. Please try again.');
    }
});

// Vote on post
async function votePost(postId, voteType) {
    try {
        const response = await fetch(`${API_URL}/posts/${postId}/vote`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({ vote_type: voteType })
        });

        if (response.ok) {
            fetchPosts();
        }
    } catch (error) {
        console.error('Error voting on post:', error);
    }
}

// Share post
async function sharePost(postId) {
    try {
        const response = await fetch(`${API_URL}/posts/${postId}/share`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });

        if (response.ok) {
            fetchPosts();
        }
    } catch (error) {
        console.error('Error sharing post:', error);
    }
}

// Populate genre select in post modal
async function populateGenreSelect() {
    try {
        const response = await fetch(`${API_URL}/genres/user`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        const genres = await response.json();
        
        postGenreSelect.innerHTML = genres.map(genre =>
            `<option value="${genre.id}">${genre.name}</option>`
        ).join('');
    } catch (error) {
        console.error('Error fetching user genres:', error);
    }
}

// Initialize
fetchPosts();
populateGenreSelect(); 