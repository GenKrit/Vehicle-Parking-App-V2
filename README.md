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
