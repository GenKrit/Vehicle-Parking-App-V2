Vehicle Parking App (MAD II Project)

Prerequisites

Before running this project, please ensure you have the following installed:

1.Node.js & npm (For Frontend)
2.Python 3.x (For Backend)
3.Redis Server (Required for Celery/Caching) - Must be running in background.
4.MailHog (For capturing emails) - Must be running.

Installation Guide

1.Backend Setup (Flask)

Open a terminal in the backend folder:
# 1. Create a virtual environment
# python -m venv venv

# 2. Activate it
# Windows:
# venv\Scripts\activate
# Mac/Linux:
# source venv/bin/activate

# 3. Install dependencies
# pip install -r requirements.txt

2. Frontend Setup (Vue.js)

Open a terminal in the frontend folder:
# Install dependencies
# npm install


How to Run the Application

You need 4 separate terminals running simultaneously.

Terminal 1: MailHog & Redis
Ensure Redis Service is running.
Run the MailHog executable.
View emails at: http://localhost:8025

Terminal 2: Flask API
# cd backend
# Ensure venv is active
# python app.py
This will automatically create the database and Admin user (admin@parking.com / admin123).

Terminal 3: Celery Worker
# cd backend
# Ensure venv is active
# celery -A app.celery worker --pool=solo --loglevel=info

Terminal 4: Celery Beat (Scheduler)
# cd backend
# Ensure venv is active
# celery -A app.celery beat --loglevel=info

Terminal 5: Frontend

# cd frontend
# npm run dev
Access the App
UI: http://localhost:5173Admin 
Login: admin@parking.com / admin123

# redis cache clear
# redis-cli FLUSHALL
