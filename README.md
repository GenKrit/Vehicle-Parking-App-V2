# Vehicle Parking App
### MAD II Project

A full-stack **Vehicle Parking Management System** developed as part of the MAD II curriculum.  
The application uses **Flask** for the backend and **Vue.js (Vite)** for the frontend, with support for authentication, background tasks, caching, and email notifications.

---

## 📌 Features

- Role-based authentication (Admin / User)
- Vehicle parking and slot management
- Admin and user dashboards
- Background task processing using Celery
- Redis-based caching
- Email notifications (MailHog for development)

---

## 🧱 Tech Stack

### Backend
- Python 3.x
- Flask
- Flask-Security
- Celery
- Redis
- SQLite

### Frontend
- Vue.js (Vite)
- Axios
- Vue Router

### Development & Utilities
- MailHog (email testing)
- Redis (cache & Celery broker)

---

## 📦 Prerequisites

Ensure the following are installed before running the project:

- **Node.js & npm** (Frontend)
- **Python 3.x** (Backend)
- **Redis Server** (must be running)
- **MailHog** (for capturing emails during development)

---

## 📁 Project Structure

```text
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

```
-----

## ⚙️ Installation

#Backend Setup (Flask)
Navigate to the backend directory and create a virtual environment:

```text
python -m venv venv
```

Activate the virtual environment:
#Windows
```text
venv\Scripts\activate
```
#macOS / Linux
```text
source venv/bin/activate
```
#Install backend dependencies:
```text
pip install -r requirements.txt
```

#Frontend Setup (Vue.js)
Navigate to the frontend directory and install dependencies:
```text
npm install
```

---

## ▶️ Running the Application (Local)
The application requires multiple services to be running simultaneously.

#Terminal 1: Redis & MailHog
- Ensure Redis service is running
- Start MailHog

#MailHog Web Interface:
http://localhost:8025

#Terminal 2: Flask API

```text
cd backend
python app.py
```

#Notes
- Database is created automatically on first run
- A default admin account is created

#Admin Credentials
- Email: admin@parking.com
- Password: admin123


# Terminal 3: Celery Worker
```text
cd backend
celery -A app.celery worker --pool=solo --loglevel=info
```

#Terminal 4: Celery Beat (Scheduler)
```text
cd backend
celery -A app.celery beat --loglevel=info
```

#Terminal 5: Frontend
```text
cd frontend
npm run dev
```

---


## 🌐 Application Access

- Frontend UI: http://localhost:5173
- #Admin Login:
- - Email: admin@parking.com
  - Password: admin123

------

##🧹 Redis Cache Management
To clear the Redis cache manually:

```text
redis-cli FLUSHALL
```

-----

##📝 Notes

- MailHog is used only for local development
- Production deployments should use an SMTP service instead of MailHog
- Celery Beat may be disabled in free-tier deployments
- Redis is required for caching and background task execution

------

##🚀 Deployment Overview

- Frontend: Vercel
- Backend: Render
- Cache / Broker: Redis (Render)

Free-tier deployments may experience cold starts.

------

##📄 License
This project is intended for academic and learning purposes.


------------------------------------------------------
