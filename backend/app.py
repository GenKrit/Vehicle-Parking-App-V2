import os
import uuid
from flask import Flask, request
from flask_cors import CORS
from flask_security import Security, SQLAlchemyUserDatastore, hash_password
from flask_security.utils import login_user as fs_login_user
from flask_caching import Cache
from flask_mail import Mail
from celery import Celery
from celery.schedules import crontab

# models & blueprints
from models.models import db, User, Role, ParkingLot
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.users import user_bp
from cache import cache

app = Flask(__name__)

# Notes to me:
# CORS: I restricted it to frontend origin so credentials + cookies work.
# We scope CORS to /api/* to be strict and avoid exposing non-API endpoints.

FRONTEND_ORIGIN = os.getenv('FRONTEND_ORIGIN', 'http://localhost:5173')
CORS(app, resources={r"/api/*": {"origins": FRONTEND_ORIGIN}}, supports_credentials=True)

# Database Config
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'parking.db')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'super-secret-key')
app.config['SECURITY_PASSWORD_SALT'] = os.getenv('SECURITY_PASSWORD_SALT', 'salt-key')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_ENABLED'] = False

# --- MILESTONE 7: REDIS CACHE CONFIG ---
app.config['CACHE_TYPE'] = 'RedisCache'
app.config['CACHE_REDIS_URL'] = os.getenv('CACHE_REDIS_URL', 'redis://localhost:6379/0')
app.config['CACHE_DEFAULT_TIMEOUT'] = 300

# --- MILESTONE 8: MAILHOG CONFIG ---
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'localhost')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 1025))
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', 'admin@parking.com')

# Initialize Extensions
db.init_app(app)
cache.init_app(app)
mail = Mail(app)

# --- CELERY CONFIG  ---
celery = Celery(
    app.name,
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
)

celery.conf.update(
    broker_url=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    result_backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
    timezone='UTC',
    enable_utc=True,
    # Scheduled Jobs (kept for testing -- adjust in production)
    beat_schedule={
        'daily-reminder': {
            'task': 'tasks.send_daily_reminder',
            'schedule': crontab(minute='*'),  # Every minute for testing
        },
        'monthly-report': {
            'task': 'tasks.generate_monthly_report',
            'schedule': crontab(minute='*/2'),  # Every 2 mins for testing
        },
    }
)

app.extensions['celery'] = celery
import tasks  

# Setup Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# --------------------------------------------------------
# -----Start of lightweight token auth (accept fs_uniquifier as Bearer token) -----
# This middleware lets the SPA send:
#     Authorization: Bearer <fs_uniquifier>
# and the server will log that user in for the request (flask-security / flask-login).
# --------------------------------------------------------
from models.models import User as UserModel  # reimport to be explicit (safe)

@app.before_request
def _accept_bearer_token_for_api():
    """
    Note to me:
    This accept Authorization: Bearer <fs_uniquifier> for SPA requests.
    Looks up User.fs_uniquifier and logs them in (request context only).
    Runs ONLY for routes under /api to avoid interfering with other endpoints.
    """
    # API requests
    if not request.path.startswith('/api'):
        return

    auth = request.headers.get('Authorization')
    if not auth:
        return

    parts = auth.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return

    token = parts[1].strip()
    if not token:
        return

    try:
        user = UserModel.query.filter_by(fs_uniquifier=token).first()
        if user:
            fs_login_user(user, remember=False)
    except Exception:
        # swallow exceptions so normal flows aren't broken
        return
_ = _accept_bearer_token_for_api  # reference to help static analyzers
# ----- END: lightweight token auth 


#  fs_uniquifier rotation helper 
# --
def rotate_fs_uniquifier(user):
    if not user:
        return None
    try:
        # Used uuid4 hex string for the token 
        user.fs_uniquifier = uuid.uuid4().hex
        db.session.add(user)
        db.session.commit()
        return user.fs_uniquifier
    except Exception:
        db.session.rollback()
        raise


# Register Blueprints 
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(admin_bp, url_prefix='/api')
app.register_blueprint(user_bp, url_prefix='/api')


# Create initial data and ensure admin gets an fs_uniquifier set
def create_initial_data():
    with app.app_context():
        db.create_all()

        # roles
        if not user_datastore.find_role('admin'):
            user_datastore.create_role(name='admin', description='Administrator')
        if not user_datastore.find_role('user'):
            user_datastore.create_role(name='user', description='Regular User')

        # admin user
        if not user_datastore.find_user(email='admin@parking.com'):
            admin_user = user_datastore.create_user(
                email='admin@parking.com',
                username='admin',
                password=hash_password('admin123'),
                roles=['admin']
            )
            # Ensure fs_uniquifier exists for token login
            if hasattr(admin_user, 'fs_uniquifier'):
                admin_user.fs_uniquifier = uuid.uuid4().hex
                db.session.add(admin_user)

        existing_admin = user_datastore.find_user(email='admin@parking.com')
        if existing_admin and hasattr(existing_admin, 'fs_uniquifier') and not existing_admin.fs_uniquifier:
            existing_admin.fs_uniquifier = uuid.uuid4().hex
            db.session.add(existing_admin)

        db.session.commit()

#added this as safeguard to prevent archieve from going  green(fre spots show)       
def repair_archive():
    with app.app_context():
        archive = ParkingLot.query.filter_by(name="Deleted - Archived History").first()
        if archive:
            print(f"Archive: Found {len(archive.spots)} spots.")
            for spot in archive.spots:
                spot.is_occupied = True # Force Red
            
            # Fix capacity to match reality so the bar makes sense
            archive.capacity = len(archive.spots) 
            
            db.session.commit()
            # A All spots marked Occupied.

if __name__ == '__main__':
    create_initial_data()
    repair_archive() # repair archieve called
    app.run(debug=True)
