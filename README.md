# 🔭 JobLens — Full Stack Job Tracker

Flask + SQLite backend with a dark-themed HTML/CSS/JS frontend.

## Project Structure

```
joblens/
├── app.py              ← Flask backend (main file)
├── joblens.db          ← SQLite database (auto-created)
├── requirements.txt
└── templates/
    ├── login.html
    ├── register.html
    └── index.html      ← Dashboard
```

## Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the server
python app.py

# 3. Open browser
http://localhost:5000
```

## API Endpoints

| Method | Endpoint          | Description              | Auth |
|--------|-------------------|--------------------------|------|
| POST   | /api/register     | New user registration    | No   |
| POST   | /api/login        | Login → returns token    | No   |
| POST   | /api/logout       | Invalidate session       | Yes  |
| GET    | /api/me           | User info + stats        | Yes  |
| GET    | /api/jobs         | Get all jobs             | Yes  |
| POST   | /api/jobs         | Add new job              | Yes  |
| DELETE | /api/jobs/:id     | Delete a job             | Yes  |
| PUT    | /api/jobs/:id     | Update job status        | Yes  |

## Authentication

Token-based auth (no JWT dependency needed):
- Login/Register → server returns a random token
- Token stored in `localStorage` on client
- Every API request sends `Authorization: Bearer <token>` header
- Tokens expire after 7 days

## Database (SQLite)

Three tables:
- `users` — email + hashed password
- `sessions` — active tokens with expiry
- `jobs` — job applications per user

Live Link: https://job-tracker-with-resume-analyzer-2.onrender.com
