from flask import Blueprint, request, jsonify, current_app
from models.models import db, ParkingLot, ParkingSpot, Reservation, User
from datetime import datetime, timezone, timedelta
from cache import cache
from zoneinfo import ZoneInfo
from sqlalchemy import func

user_bp = Blueprint('user', __name__)

# Utilities 
def _ensure_aware(dt):
    """
    Ensure a datetime is timezone-aware in UTC.
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _format_reservation_for_client(reservation, ist_tz):
    """
    Convert a Reservation DB object into the exact shape expected by the frontend.
    """
    now_utc = datetime.now(timezone.utc)
    start_utc = _ensure_aware(reservation.start_time)
    end_utc = _ensure_aware(reservation.end_time)

    if start_utc is None:
        return None

    if end_utc:
        delta = end_utc - start_utc
    else:
        delta = now_utc - start_utc

    hours = int(delta.total_seconds() // 3600)
    minutes = int((delta.total_seconds() % 3600) // 60)
    duration_str = f"{hours}h {minutes}m"

    # convert UTC -> IST for display strings
    start_local = start_utc.astimezone(ist_tz)
    end_local = end_utc.astimezone(ist_tz) if end_utc else None

    start_str = start_local.strftime("%Y-%m-%d %H:%M")
    end_str = end_local.strftime("%Y-%m-%d %H:%M") if end_local else "-"

    return {
        "id": reservation.id,
        "spot": reservation.spot.spot_number,
        "lot": reservation.spot.parking_lot.name,
        "start_time": start_str,
        "end_time": end_str,
        #  TIMESTAMPS FOR SORTING 
        "start_ts": start_utc.isoformat(),
        "end_ts": end_utc.isoformat() if end_utc else None,

        "duration": duration_str,
        "cost": float(reservation.total_cost or 0.0),
        "active": bool(reservation.active)
    }

# AVAILABLE LOTS (cached) 
@user_bp.route('/available-lots', methods=['GET'])
@cache.cached(timeout=60, key_prefix='available_lots')
def get_available_lots():
    lots = ParkingLot.query.options().all()
    output = []
    for lot in lots:
        available_spots = sum(1 for s in lot.spots if not s.is_occupied)
        if available_spots > 0:
            data = {
                'id': lot.id,
                'name': lot.name,
                'address': lot.address,
                'price_per_hour': float(lot.price_per_hour or 0.0),
                'available_spots': available_spots
            }
            if hasattr(lot, 'pin_code'):
                data['pin_code'] = getattr(lot, 'pin_code', None)
            output.append(data)
    return jsonify(output), 200


# TRIGGER CSV EXPORT
@user_bp.route('/export-csv', methods=['POST'])
def trigger_export():
    data = request.get_json() or {}
    email = data.get('email')
    if not email:
        return jsonify({'message': 'email required'}), 400

    try:
        current_app.extensions['celery'].send_task('tasks.export_user_csv', args=[email])
    except Exception:
        current_app.logger.exception("Failed to trigger export task")
        return jsonify({'message': 'Failed to start export'}), 500

    return jsonify({'message': 'Export started. Check your email.'}), 200


# RESERVE - multiple quantity bookings (1..10)
@user_bp.route('/reserve', methods=['POST'])
def reserve_spot():
    data = request.get_json() or {}
    lot_id = data.get('lot_id')
    user_email = data.get('user_email')

    try:
        quantity = int(data.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1
    quantity = max(1, min(10, quantity))

    user = User.query.filter_by(email=user_email).first()
    if not user:
        return jsonify({'message': 'User not found'}), 404

    lot = ParkingLot.query.get(lot_id)
    if not lot:
        return jsonify({'message': 'Lot not found'}), 404

    free_spots = (
        ParkingSpot.query
        .filter_by(lot_id=lot_id, is_occupied=False)
        .order_by(ParkingSpot.id)
        .limit(quantity)
        .with_for_update(read=True)
        .all()
    )

    if len(free_spots) == 0:
        return jsonify({'message': 'Lot full'}), 400

    if len(free_spots) < quantity:
        return jsonify({
            'message': f'Only {len(free_spots)} spots available in this lot.',
            'available': len(free_spots)
        }), 400

    now_utc = datetime.now(timezone.utc)
    created_reservations = []

    try:
        for spot in free_spots:
            spot.is_occupied = True
            reservation = Reservation(
                user_id=user.id,
                spot_id=spot.id,
                start_time=now_utc,
                active=True
            )
            db.session.add(reservation)

        db.session.flush()
        spot_ids = [s.id for s in free_spots]
        db.session.commit()

        created = (
            Reservation.query
            .filter(Reservation.user_id == user.id,
                    Reservation.spot_id.in_(spot_ids),
                    Reservation.start_time == now_utc)
            .all()
        )

        for r in created:
            created_reservations.append({
                'reservation_id': r.id,
                'spot': r.spot.spot_number
            })

        cache.delete('available_lots')
        cache.delete('admin_analytics')

        return jsonify({
            'message': 'Success!',
            'reservations': created_reservations
        }), 201

    except Exception:
        db.session.rollback()
        try:
            for s_id in [s.id for s in free_spots]:
                sp = ParkingSpot.query.get(s_id)
                if sp:
                    sp.is_occupied = False
            db.session.commit()
        except Exception:
            db.session.rollback()

        current_app.logger.exception("Error creating multiple reservations")
        return jsonify({'message': 'Internal server error'}), 500


# MY RESERVATIONS
@user_bp.route('/my-reservations', methods=['POST'])
def my_reservations():
    data = request.get_json() or {}
    email = data.get('email')
    if not email:
        return jsonify([]), 200

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify([]), 200

    ist = ZoneInfo("Asia/Kolkata")
    reservations = Reservation.query.filter_by(user_id=user.id).order_by(Reservation.start_time.desc()).all()

    output = []
    for r in reservations:
        formatted = _format_reservation_for_client(r, ist)
        if formatted:
            output.append(formatted)

    return jsonify(output), 200


# RELEASE: end a reservation and compute cost
@user_bp.route('/release-spot', methods=['POST'])
def release_spot():
    data = request.get_json() or {}
    reservation_id = data.get('reservation_id')
    reservation = Reservation.query.get(reservation_id)
    if not reservation or not reservation.active:
        return jsonify({'message': 'Invalid reservation'}), 400

    end_time = datetime.now(timezone.utc)
    start_time = _ensure_aware(reservation.start_time)
    if start_time is None:
        return jsonify({'message': 'Invalid reservation data'}), 400

    duration_seconds = (end_time - start_time).total_seconds()
    hours = max(1, duration_seconds / 3600.0)

    price = float(reservation.spot.parking_lot.price_per_hour or 0.0)
    cost = round(hours * price, 2)

    reservation.end_time = end_time
    reservation.total_cost = cost
    reservation.active = False
    reservation.spot.is_occupied = False

    db.session.commit()

    cache.delete('available_lots')
    cache.delete('admin_analytics')

    return jsonify({'message': 'Spot Released', 'cost': cost}), 200


# Analytics endpoints
# ----------------------------

@user_bp.route('/user-summary', methods=['POST'])
def user_summary():
    """
    Provide summary data for the user's Summary tab.
    Fixed: Performs date grouping in Python to avoid SQLite 'func.date' crashes.
    """
    data = request.get_json() or {}
    email = data.get('email')
    if not email:
        return jsonify({'message': 'email required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({
            'total_spent': 0.0,
            'per_lot': [],
            'timeseries_30d': [],
            'lots_list': []
        }), 200

    # Total Spent
    total_spent = db.session.query(
        func.coalesce(func.sum(Reservation.total_cost), 0.0)
    ).filter(
        Reservation.user_id == user.id,
        Reservation.total_cost != None
    ).scalar() or 0.0

    # Per-Lot Aggregation
    per_lot_rows = db.session.query(
        ParkingLot.id,
        ParkingLot.name,
        func.coalesce(func.sum(Reservation.total_cost), 0.0)
    ).join(ParkingSpot, ParkingSpot.lot_id == ParkingLot.id
    ).join(Reservation, Reservation.spot_id == ParkingSpot.id
    ).filter(
        Reservation.user_id == user.id,
        Reservation.total_cost != None
    ).group_by(ParkingLot.id, ParkingLot.name).all()

    per_lot = [{
        'lot_id': row[0],
        'lot_name': row[1],
        'total_spent': float(row[2])
    } for row in per_lot_rows]

    # Timeseries (Last 30 Days) - PYTHON GROUPING
    today_utc = datetime.now(timezone.utc).date()
    start_date = today_utc - timedelta(days=29)
    
    # last 30 days
    ts_map = { (start_date + timedelta(days=i)).isoformat(): 0.0 for i in range(30) }

    # new reservations
    recent_res = Reservation.query.filter(
        Reservation.user_id == user.id,
        Reservation.total_cost != None,
        Reservation.end_time >= start_date
    ).all()

    for r in recent_res:
        if r.end_time:
            d_str = r.end_time.strftime('%Y-%m-%d')
            if d_str in ts_map:
                ts_map[d_str] += float(r.total_cost or 0.0)

    timeseries_30d = [{'date': d, 'amount': round(ts_map[d], 2)} for d in sorted(ts_map.keys())]

    # Lots list for dropdowns
    lots_list = [{'id': l.id, 'name': l.name} for l in ParkingLot.query.order_by(ParkingLot.name).all()]

    return jsonify({
        'total_spent': float(total_spent),
        'per_lot': per_lot,
        'timeseries_30d': timeseries_30d,
        'lots_list': lots_list
    }), 200


@user_bp.route('/parking-lot/<int:lot_id>/analytics', methods=['POST'])
def parking_lot_analytics(lot_id):
    """
    Per-lot analytics scoped to the requesting user.
    Fixed: Performs date grouping in Python.
    """
    data = request.get_json() or {}
    email = data.get('email')
    if not email:
        return jsonify({'message': 'email required'}), 400

    user = User.query.filter_by(email=email).first()
    lot = ParkingLot.query.get(lot_id)
    if not user or not lot:
        return jsonify({'message': 'not found'}), 404

    # Total revenue for this lot (user specific)
    total_revenue = db.session.query(func.coalesce(func.sum(Reservation.total_cost), 0.0)).join(
        ParkingSpot, ParkingSpot.id == Reservation.spot_id
    ).filter(
        Reservation.user_id == user.id,
        ParkingSpot.lot_id == lot_id,
        Reservation.total_cost != None
    ).scalar() or 0.0

    today_utc = datetime.now(timezone.utc).date()
    start_date = today_utc - timedelta(days=29)


    # fetch all relevant reservations first to avoid complex date logic in SQL
    all_res_for_lot = Reservation.query.join(ParkingSpot).filter(
        Reservation.user_id == user.id,
        ParkingSpot.lot_id == lot_id
    ).all()

    todays_bookings = 0
    months_bookings = 0
    
    # Timeseries
    ts_map = { (start_date + timedelta(days=i)).isoformat(): 0.0 for i in range(30) }

    # Avg Duration
    total_seconds = 0
    count_completed = 0

    for r in all_res_for_lot:
        if not r.start_time: continue
        
        st_date = r.start_time.date() if r.start_time else None
        
        if st_date == today_utc:
            todays_bookings += 1
        
        if st_date and st_date >= start_date:
            months_bookings += 1

        # Revenue Timeseries 
        if r.end_time and r.total_cost is not None:
            et_date_str = r.end_time.strftime('%Y-%m-%d')
            if et_date_str in ts_map:
                ts_map[et_date_str] += float(r.total_cost)
            
            # Duration
            dur = (r.end_time - r.start_time).total_seconds()
            if dur > 0:
                total_seconds += dur
                count_completed += 1

    avg_minutes = 0
    if count_completed > 0:
        avg_minutes = int(round((total_seconds / count_completed) / 60.0))

    timeseries_30d = [{'date': d, 'revenue': round(ts_map[d], 2)} for d in sorted(ts_map.keys())]

    return jsonify({
        'lot_id': lot.id,
        'lot_name': lot.name,
        'total_revenue': float(total_revenue),
        'todays_bookings': todays_bookings,
        'months_bookings': months_bookings,
        'avg_duration_minutes': avg_minutes,
        'timeseries_30d': timeseries_30d
    }), 200