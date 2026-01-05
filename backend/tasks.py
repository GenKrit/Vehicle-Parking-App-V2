from app import celery
from models.models import User, Reservation
from flask_mail import Message
import csv
import io
from datetime import datetime
from sqlalchemy import func

# JOB A: Daily Reminder
@celery.task
def send_daily_reminder():
    """Check if user has no active reservation to remind user."""
    # Imported locally to avoid circular dependency
    from app import app, mail 
    with app.app_context():
        users = User.query.all()
        count = 0
        for user in users:
            if user.has_role('admin'): continue

            # Check for active spot
            has_active = Reservation.query.filter_by(user_id=user.id, active=True).first()
            
            if not has_active:
                msg = Message("Need Parking Tomorrow?", recipients=[user.email])
                msg.body = f"Hi {user.username},\n\nYou don't have a spot booked. Log in now to reserve one!"
                mail.send(msg)
                count += 1
        return f"Daily Reminders sent to {count} users."

# JOB B: Monthly Activity Report
@celery.task
def generate_monthly_report():
    """Send HTML report of current month's bookings to Admin."""
    from app import app, mail 
    with app.app_context():
        now = datetime.utcnow()
        # Filter for current month
        reservations = Reservation.query.filter(
            func.extract('month', Reservation.start_time) == now.month,
            func.extract('year', Reservation.start_time) == now.year
        ).all()

        total_revenue = sum(r.total_cost for r in reservations)
        
        # HTML Content
        html = f"<h1>Monthly Report: {now.strftime('%B %Y')}</h1>"
        html += f"<p>Total Revenue: <strong>₹{total_revenue}</strong></p><ul>"
        for r in reservations:
            html += f"<li>User: {r.user.email} | Spot: {r.spot.spot_number} | Cost: ₹{r.total_cost}</li>"
        html += "</ul>"

        msg = Message(f"Monthly Report - {now.strftime('%B')}", recipients=['admin@parking.com'])
        msg.html = html
        mail.send(msg)
        return "Monthly Report Sent"

# JOB C: Export CSV (Async)
@celery.task
def export_user_csv(user_email):
    """Generate CSV of user history and email it."""
    from app import app, mail 
    with app.app_context():
        user = User.query.filter_by(email=user_email).first()
        if not user: return "User Not Found"

        # Generate CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Reservation ID', 'Lot', 'Spot', 'Start', 'End', 'Cost', 'Status'])

        reservations = Reservation.query.filter_by(user_id=user.id).all()
        for r in reservations:
            status = "Active" if r.active else "Completed"
            writer.writerow([r.id, r.spot.parking_lot.name, r.spot.spot_number, r.start_time, r.end_time, r.total_cost, status])
        
        output.seek(0)

        # Send Email
        msg = Message("Your Parking History Export", recipients=[user_email])
        msg.body = "Please find the CSV export attached in this email."
        msg.attach("parking_history.csv", "text/csv", output.getvalue())
        
        mail.send(msg)
        return f"CSV sent to {user_email}"