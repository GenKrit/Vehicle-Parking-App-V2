# 🚗 Vehicle Parking App
MAD II Project

A full-stack Vehicle Parking Management System built using Flask and Vue.js.
The application supports role-based access, background task processing,
caching, and email notifications.

--------------------------------------------------
TECH STACK
--------------------------------------------------

Backend:
- Python 3.x
- Flask
- Flask-Security
- Celery
- Redis
- SQLite

Frontend:
- Vue.js (Vite)
- Axios
- Vue Router

Development Tools:
- MailHog (email testing)
- Redis (cache + Celery broker)

--------------------------------------------------
PREREQUISITES
--------------------------------------------------

Before running this project, ensure the following are installed:

1. Node.js & npm (Frontend)
2. Python 3.x (Backend)
3. Redis Server (must be running)
4. MailHog (for capturing emails during development)

--------------------------------------------------
PROJECT STRUCTURE
--------------------------------------------------

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

--------------------------------------------------
INSTALLATION GUIDE
--------------------------------------------------

BACKEND SETUP (Flask)

Open a terminal in the backend folder:

1. Create a virtual environment
   python -m venv venv

2. Activate the virtual environment

   Windows:
   venv\Scripts\activate

   macOS / Linux:
   source venv/bin/activate

3. Install dependencies
   pip install -r requirements.txt

--------------------------------------------------

FRONTEND SETUP (Vue.js)

Open a terminal in the frontend folder:

1. Install dependencies
   npm install

--------------------------------------------------
RUNNING THE APPLICATION (LOCAL)
--------------------------------------------------

You need multiple terminals running simultaneously.

--------------------------------------------------
TERMINAL 1: Redis & MailHog
--------------------------------------------------

- Ensure Redis service is running
- Start MailHog

MailHog UI:
http://localhost:8025

--------------------------------------------------
TERMINAL 2: Flask API
--------------------------------------------------

cd backend
python app.py

Notes:
- Database is created automatically
- Default admin user is created

Admin Credentials:
Email: admin@parking.com
Password: admin123

--------------------------------------------------
TERMINAL 3: Celery Worker
--------------------------------------------------

cd backend
celery -A app.celery worker --pool=solo --loglevel=info

--------------------------------------------------
TERMINAL 4: Celery Beat (Scheduler)
--------------------------------------------------

cd backend
celery -A app.celery beat --loglevel=info

--------------------------------------------------
TERMINAL 5: Frontend
--------------------------------------------------

cd frontend
npm run dev

--------------------------------------------------
ACCESSING THE APPLICATION
--------------------------------------------------

Frontend UI:
http://localhost:5173

Admin Login:
Email: admin@parking.com
Password: admin123

--------------------------------------------------
REDIS CACHE MANAGEMENT
--------------------------------------------------

To clear Redis cache manually:

redis-cli FLUSHALL

--------------------------------------------------
NOTES
--------------------------------------------------

- MailHog is used only for local development.
- For production deployment, SMTP services should replace MailHog.
- Celery Beat may be disabled in free-tier deployments.
- Redis is required for caching and background task processing.

--------------------------------------------------
