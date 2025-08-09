# Blog Post Web Application

A minimalist blog post web application with user authentication and topic-based posting system.

## Project Structure
```
.
├── frontend/           # Frontend static files
│   ├── index.html     # Main page
│   ├── css/           # CSS styles
│   ├── js/            # JavaScript files
│   └── pages/         # Additional HTML pages
└── backend/           # Python backend
    ├── app.py         # Main application file
    ├── config.py      # Configuration
    ├── models/        # Database models
    └── routes/        # API routes
```

## Setup Instructions

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up MySQL database:
   - Create a new MySQL database
   - Update database configuration in backend/.env file

3. Run the backend server:
   ```bash
   cd backend
   python app.py
   ```

4. Open the frontend:
   - Open frontend/index.html in your web browser
   - For development, you can use a simple HTTP server:
     ```bash
     cd frontend
     python -m http.server 8000
     ```

## Features
- User authentication (signup/login)
- Topic/genre selection (minimum 3)
- Blog post creation and management
- Upvoting/downvoting system
- Comments and sharing functionality 