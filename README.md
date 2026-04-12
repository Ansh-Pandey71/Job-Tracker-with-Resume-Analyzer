# 🔭 JobLens — Smart Job Tracker & Resume Analyzer

JobLens is a full-stack web application designed to help students and job seekers efficiently track their job applications and improve their resumes through structured analysis.


🔍 Problem Statement

The modern job search process is fragmented and inefficient:
Applications are scattered across platforms
No centralized tracking system
Lack of feedback on resume quality
Missed opportunities due to poor organization

💡 Solution

JobLens provides a unified platform where users can:
Track all job applications in one place
Analyze resumes against job descriptions
Identify missing skills and improve job readiness

✨ Key Features
📌 Job Application Tracker (Add, update, delete applications)
📊 Dashboard with application overview
🧠 Resume Analyzer (basic keyword matching & skill gap detection)
🔐 Secure Authentication (token-based session system)

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

🛠 Tech Stack

Frontend: HTML, CSS, JavaScript
Backend: Flask (Python)
Database: SQLite
Deployment: Render

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
  

🔗 Live Application
👉 https://job-tracker-with-resume-analyzer-2.onrender.com

💻 GitHub Repository
👉 https://github.com/Ansh-Pandey71/Job-Tracker-with-Resume-Analyzer

📽 Explainer Video
👉 https://drive.google.com/file/d/1B5khOluOrKCyDyOpJvhn3_XfJl206-71/view?usp=drivesdk

📊 Project Presentation
👉 https://drive.google.com/file/d/1moqFjnn-UTYOkNtOrikL23XgxaxJUv0A/view?usp=sharing 

👉 https://docs.google.com/presentation/d/1GgdIITROyD544lk9LyttARFHuehygVQE/edit?usp=sharing&ouid=102310430955649078200&rtpof=true&sd=true
