🚗 Vehicle Parking App
MAD II Project

A full-stack Vehicle Parking Management System built using Flask (backend) and Vue.js (frontend).
The application supports role-based access, background task processing, caching, and email notifications.

✨ Features

Role-based authentication (Admin / User)

Vehicle parking management

Admin and user dashboards

Background tasks using Celery

Redis-based caching

Email notifications (MailHog for development)

🧱 Tech Stack
Backend

Python 3.x

Flask

Flask-Security

Celery

Redis

SQLite

Frontend

Vue.js (Vite)

Axios

Vue Router

Development Tools

MailHog (email testing)

Redis (cache & Celery broker)

📦 Prerequisites

Make sure the following are installed before running the project:

Node.js & npm (Frontend)

Python 3.x (Backend)

Redis Server (must be running)

MailHog (for capturing emails during development)

📁 Project Structure
.
├── backend
│   ├── app.py
│   ├── cache.py
│   ├── tasks.py
│   ├── requirements.txt
│   ├── models
│   │   └── models.py
│   └── routes
│       ├── admin.py
│       ├── auth.py
│       └── users.py
│
├── frontend
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src
│       ├── api.js
│       ├── App.vue
│       ├── main.js
│       ├── router
│       │   └── index.js
│       └── views
│           ├── AdminDashboard.vue
│           ├── UserDashboard.vue
│           ├── LoginView.vue
│           ├── RegisterView.vue
│           └── ProfileView.vue
│
├── openapi.yaml
└── README.md

⚙️ Installation
Backend Setup (Flask)

Open a terminal in the backend folder:

python -m venv venv


Activate the virtual environment:

Windows

venv\Scripts\activate


macOS / Linux

source venv/bin/activate


Install dependencies:

pip install -r requirements.txt

Frontend Setup (Vue.js)

Open a terminal in the frontend folder:

npm install

▶️ Running the Application (Local)

You will need multiple terminals running simultaneously.

Terminal 1: Redis & MailHog

Ensure Redis service is running

Start MailHog

MailHog Web UI:
👉 http://localhost:8025

Terminal 2: Flask API
cd backend
python app.py


Notes:

Database is created automatically

Default admin user is created on first run

Admin Credentials

Email: admin@parking.com

Password: admin123

Terminal 3: Celery Worker
cd backend
celery -A app.celery worker --pool=solo --loglevel=info

Terminal 4: Celery Beat (Scheduler)
cd backend
celery -A app.celery beat --loglevel=info

Terminal 5: Frontend
cd frontend
npm run dev

🌐 Access the Application

Frontend UI: http://localhost:5173

Admin Login:

Email: admin@parking.com

Password: admin123

🧹 Redis Cache Management

To clear Redis cache manually:

redis-cli FLUSHALL

📝 Notes

MailHog is used only for local development

For production, MailHog should be replaced with an SMTP service

Celery Beat may be disabled in free-tier deployments

Redis is required for caching and background task execution

📌 Deployment

This project can be deployed using:

Frontend: Vercel

Backend: Render

Cache / Broker: Redis (Render)

Free-tier deployments may experience cold starts.
