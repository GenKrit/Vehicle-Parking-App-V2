Vehicle Parking App
Modern full-stack vehicle parking management system built with Vue.js and Flask.

Tech Stack
Frontend: Vue.js
Backend: Flask (Python)
Task Queue: Celery + Redis
Email Testing: MailHog
Database: SQLite (auto-generated)

Prerequisites
Ensure the following are installed on your system:

Node.js & npm (v16+)

Python 3.x

Redis Server

MailHog

Installation
Backend Setup
Navigate to the backend directory and set up the Python environment:

bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
Frontend Setup
Navigate to the frontend directory and install dependencies:

bash
cd frontend
npm install
Running the Application
The application requires 5 terminals running simultaneously.

Terminal 1: Redis & MailHog
Start Redis service (ensure it's running in the background).

Run MailHog executable and access the email interface at http://localhost:8025

Terminal 2: Flask API Server
bash
cd backend
# Activate venv first
python app.py
The database and admin user will be created automatically on first run.

Terminal 3: Celery Worker
bash
cd backend
# Activate venv first
celery -A app.celery worker --pool=solo --loglevel=info
Terminal 4: Celery Beat Scheduler
bash
cd backend
# Activate venv first
celery -A app.celery beat --loglevel=info
Terminal 5: Vue.js Frontend
bash
cd frontend
npm run dev
Access Points
Application UI: http://localhost:5173

Email Interface: http://localhost:8025

Default Admin Credentials
Email: admin@parking.com

Password: admin123

Useful Commands
Clear Redis Cache
bash
redis-cli FLUSHALL
Stop All Services
Press Ctrl+C in each terminal to gracefully stop the services.

Project Structure
text
vehicle-parking-app/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── venv/
├── frontend/
│   ├── src/
│   ├── package.json
│   └── node_modules/
└── README.md
Troubleshooting
Redis Connection Error: Ensure Redis service is running before starting Celery workers.

Port Already in Use: Check if another service is using ports 5173, 5000, or 8025.

Database Issues: Delete the existing database file and restart the Flask server to recreate it.

Would you like me to add sections for API documentation, features list, or deployment instructions?

in code bash way to directly paste
3 steps completed
I'll reformat it with easily copyable code blocks that you can paste directly into your terminal:

Vehicle Parking App
Modern full-stack vehicle parking management system built with Vue.js and Flask.

Tech Stack
Frontend: Vue.js
Backend: Flask (Python)
Task Queue: Celery + Redis
Email Testing: MailHog
Database: SQLite (auto-generated)

Prerequisites
Ensure the following are installed on your system:

Node.js & npm (v16+)

Python 3.x

Redis Server

MailHog

Installation
Backend Setup
bash
cd backend
Windows:

bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
Mac/Linux:

bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
Frontend Setup
bash
cd frontend
npm install
Running the Application
The application requires 5 terminals running simultaneously.

Terminal 1: Redis & MailHog
Start Redis service in background, then run MailHog executable.

Access: http://localhost:8025

Terminal 2: Flask API Server
Windows:

bash
cd backend
venv\Scripts\activate
python app.py
Mac/Linux:

bash
cd backend
source venv/bin/activate
python app.py
Terminal 3: Celery Worker
Windows:

bash
cd backend
venv\Scripts\activate
celery -A app.celery worker --pool=solo --loglevel=info
Mac/Linux:

bash
cd backend
source venv/bin/activate
celery -A app.celery worker --pool=solo --loglevel=info
Terminal 4: Celery Beat Scheduler
Windows:

bash
cd backend
venv\Scripts\activate
celery -A app.celery beat --loglevel=info
Mac/Linux:

bash
cd backend
source venv/bin/activate
celery -A app.celery beat --loglevel=info
Terminal 5: Vue.js Frontend
bash
cd frontend
npm run dev
Access Points
Service	URL
Application UI	http://localhost:5173
Email Interface	http://localhost:8025
Default Admin Credentials
text
Email: admin@parking.com
Password: admin123
Useful Commands
Clear Redis Cache
bash
redis-cli FLUSHALL
Deactivate Virtual Environment
bash
deactivate
Check Redis Status
Windows:

bash
redis-cli ping
Mac/Linux:

bash
redis-cli ping
Project Structure
text
vehicle-parking-app/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── venv/
├── frontend/
│   ├── src/
│   ├── package.json
│   └── node_modules/
└── README.md
Troubleshooting
Redis Connection Error: Ensure Redis service is running before starting Celery workers.

Port Already in Use: Check if another service is using ports 5173, 5000, or 8025.

Database Issues: Delete the existing database file and restart the Flask server to recreate it.
