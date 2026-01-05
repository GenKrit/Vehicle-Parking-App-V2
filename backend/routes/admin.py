from flask import Blueprint, request, jsonify
from models.models import db, User, ParkingLot, ParkingSpot, Reservation
from cache import cache
from datetime import datetime, date, timedelta, timezone

import time
from sqlalchemy import func, and_, not_ 

admin_bp = Blueprint('admin', __name__)



# Helper: close & bill a reservation, free its spot

def _close_and_bill_reservation(reservation):
    """
    Note for me:- 
    This fn closes an active reservation, compute cost based on current lot price,
    and free the associated spot. Returns the billed amount.
    Used UTC everywhere and handles naive datetimes defensively.
    """
    if not reservation or not reservation.active:
        return 0.0

    end_time = datetime.now(timezone.utc)

    start_time = reservation.start_time
    if start_time is None:
        start_time = end_time

    if getattr(start_time, 'tzinfo', None) is None:
        
        start_time = start_time.replace(tzinfo=timezone.utc)
    else:
        start_time = start_time.astimezone(timezone.utc)

    duration = end_time - start_time
    hours = max(1.0, duration.total_seconds() / 3600.0)
    # minutes = max(1, duration.total_seconds() / 60)

    # defensive retrieval of rate
    rate = 0.0
    try:
        if reservation.spot and reservation.spot.parking_lot:
            rate = float(reservation.spot.parking_lot.price_per_hour or 0.0)
    except Exception:
        rate = float(getattr(reservation, 'rate', 0.0) or 0.0)

    cost = round(hours * rate, 2)
    # cost = round((minutes / 60) * rate, 2)

    reservation.end_time = end_time
    reservation.total_cost = cost
    reservation.active = False

    # free the spot if relationship exists
    try:
        if reservation.spot:
            reservation.spot.is_occupied = False
    except Exception:
        
        pass

    return cost


# --
# Parking lots: list
# --

@admin_bp.route('/parking-lots', methods=['GET'])
def get_parking_lots():
    lots = ParkingLot.query.all()
    
    archive_name = "Deleted - Archived History"
    
    # Sort: Normal lots (0) first, Archive (1) last. Secondary sort by ID.
    sorted_lots = sorted(lots, key=lambda x: (1 if x.name == archive_name else 0, x.id))

    output = []
    
    for lot in sorted_lots:   
        try:
            ordered_spots = sorted(lot.spots, key=lambda s: s.spot_number)
        except Exception:
            ordered_spots = list(lot.spots)

        output.append({
            'id': lot.id,
            'name': lot.name,
            'address': lot.address,
            'pin_code': lot.pin_code,
            'capacity': lot.capacity,
            'price_per_hour': lot.price_per_hour,
            'active_spots': len([s for s in lot.spots if not s.is_occupied]),
            'spots': [
                {
                    'id': s.id,
                    'spot_number': s.spot_number,
                    'is_occupied': s.is_occupied,
                }
                for s in ordered_spots
            ],
        })
    return jsonify(output), 200


# Parking lots: create
# --
@admin_bp.route('/parking-lot', methods=['POST'])
def create_parking_lot():
    data = request.get_json() or {}

    try:
        capacity = int(data.get('capacity'))
        price = float(data.get('price_per_hour'))
    except (TypeError, ValueError):
        return jsonify({'message': 'Invalid capacity or price_per_hour'}), 400

    new_lot = ParkingLot(
        name=data.get('name'),
        address=data.get('address'),
        pin_code=data.get('pin_code'),
        capacity=capacity,
        price_per_hour=price
    )

    db.session.add(new_lot)
    db.session.flush()  #

    for i in range(1, capacity + 1):
        new_spot = ParkingSpot(
            spot_number=f"{(data.get('name') or '')[:3].upper()}-{i}",
            lot_id=new_lot.id
        )
        db.session.add(new_spot)

    db.session.commit()

    cache.delete('available_lots')
    cache.delete('admin_analytics')

    return jsonify({'message': 'Created'}), 201


# Parking lots: update lot (edit lot details + capacity logic)
# --
@admin_bp.route('/parking-lot/<int:id>', methods=['PUT'])
def update_parking_lot(id):
    lot = ParkingLot.query.get(id)
    if not lot:
        return jsonify({'message': 'Parking lot not found'}), 404
    
    # --- NEW CHECK: Block editing the Archive ---
    if lot.name == "Deleted - Archived History":
        return jsonify({'message': 'System Archive cannot be edited.'}), 403

    data = request.get_json() or {}
    lot.name = data.get('name', lot.name)
    lot.address = data.get('address', lot.address)
    lot.pin_code = data.get('pin_code', lot.pin_code)

    if 'price_per_hour' in data and data['price_per_hour'] != '':
        try:
            lot.price_per_hour = float(data['price_per_hour'])
        except ValueError:
            return jsonify({'message': 'Invalid price_per_hour value'}), 400

    # Capacity handling
    new_capacity_raw = data.get('capacity', None)
    if new_capacity_raw is not None and new_capacity_raw != '':
        try:
            new_capacity = int(new_capacity_raw)
        except ValueError:
            return jsonify({'message': 'Invalid capacity value'}), 400

        if new_capacity < 1:
            return jsonify({'message': 'Capacity must be at least 1'}), 400

        current_capacity = lot.capacity or 0
        occupied_count = len([s for s in lot.spots if s.is_occupied])

        # Cannot shrink below number of occupied spots
        if new_capacity < occupied_count:
            return jsonify({
                'message': (
                    f'Cannot reduce capacity below {occupied_count} '
                    f'because {occupied_count} spots are currently occupied.'
                )
            }), 400

        # Increase capacity 
        if new_capacity > current_capacity:
            for i in range(current_capacity + 1, new_capacity + 1):
                spot_num = f"{lot.name[:3].upper()}-{i}"
                db.session.add(ParkingSpot(spot_number=spot_num, lot_id=lot.id))

        # Decrease capacity (but still >= occupied_count) -> remove free spots
        elif new_capacity < current_capacity:
            free_spots = [s for s in lot.spots if not s.is_occupied]
            free_spots.sort(key=lambda s: s.id, reverse=True)
            to_remove = current_capacity - new_capacity

            if to_remove > len(free_spots):
                return jsonify({
                    'message': 'Not enough free spots to reduce capacity safely.'
                }), 400

            for s in free_spots[:to_remove]:
                db.session.delete(s)

        lot.capacity = new_capacity

    db.session.commit()
    cache.delete('available_lots')
    cache.delete('admin_analytics')

    return jsonify({'message': 'Parking lot updated successfully'}), 200


# --
# Parking lots: delete (SAFE ONLY – no force delete)


# -- Older code -- deletes lot and reservation history causing cost malfunction

# @admin_bp.route('/parking-lot/<int:id>', methods=['DELETE'])
# def delete_parking_lot(id):
#     lot = ParkingLot.query.get(id)
#     if not lot:
#         return jsonify({'message': 'Parking lot not found'}), 404

#     # 1. Check for ACTIVE reservations 
#     active_reservations = (
#         Reservation.query
#         .join(ParkingSpot, Reservation.spot_id == ParkingSpot.id)
#         .filter(ParkingSpot.lot_id == lot.id, Reservation.active.is_(True))
#         .first()
#     )

#     if active_reservations:
#         return jsonify({
#             'message': 'Cannot delete: Lot has active (ongoing) reservations.',
#         }), 400

#     try:
#        #Delete all PAST reservations associated with this lot
#         spot_ids = [s.id for s in lot.spots]
        
#         if spot_ids:
#             # Delete all reservations (history) linked to these spots
#             Reservation.query.filter(Reservation.spot_id.in_(spot_ids)).delete(synchronize_session=False)

        
#         db.session.delete(lot)
#         db.session.commit()

#         # Clear caches
#         cache.delete('available_lots')
#         cache.delete('admin_analytics')

#         return jsonify({'message': 'Parking lot and its history deleted successfully.'}), 200

#     except Exception as e:

#         db.session.rollback()
#         print("Delete Error:", str(e)) 
#         return jsonify({'message': 'Database error while deleting.'}), 500


# -- New code to handle deletion by deleting storage but archieving lot and keeping spot info for analytics 
@admin_bp.route('/parking-lot/<int:id>', methods=['DELETE'])
def delete_parking_lot(id):
    lot = ParkingLot.query.get(id)
    if not lot:
        return jsonify({'message': 'Parking lot not found'}), 404
    
    # Stop ARCHIVE deletion 
    if lot.name == "Deleted - Archived History":
        return jsonify({'message': 'System Archive cannot be deleted.'}), 403

    active_reservations = (
        Reservation.query
        .join(ParkingSpot, Reservation.spot_id == ParkingSpot.id)
        .filter(ParkingSpot.lot_id == lot.id, Reservation.active.is_(True))
        .first()
    )

    if active_reservations:
        return jsonify({
            'message': 'Cannot delete: Lot has active (ongoing) sessions.',
        }), 400

    try:

        
        has_history = (
            Reservation.query
            .join(ParkingSpot, Reservation.spot_id == ParkingSpot.id)
            .filter(ParkingSpot.lot_id == lot.id)
            .first()
        )

        if has_history:
            # Get or Create Archive Lot
            archive_name = "Deleted - Archived History"
            archive_lot = ParkingLot.query.filter_by(name=archive_name).first()
            
            if not archive_lot:
                archive_lot = ParkingLot(
                    name=archive_name,
                    address="Deleted Data Storage",
                    pin_code="000000",
                    capacity=0,
                    price_per_hour=0.0
                )
                db.session.add(archive_lot)
                db.session.commit()

            spots_to_move = list(lot.spots) 
            
            for spot in spots_to_move:
                # Rename spot to indicate deletion
                #timestamp to avoid a "Duplicate Name" error
                unique_suffix = str(int(time.time()))
                new_name = f"{lot.name[:5]}_{spot.spot_number}_{unique_suffix}"
                
                spot.spot_number = new_name[:20] # Truncate to fit DB limit
                spot.lot_id = archive_lot.id
                spot.is_occupied = True 

            # commit to detach the spots from db
            db.session.commit()


        db.session.delete(lot)
        db.session.commit()

        cache.delete('available_lots')
        cache.delete('admin_analytics')

        return jsonify({'message': 'Parking lot deleted successfully.'}), 200

    except Exception as e:
        db.session.rollback()
        print("DELETE ERROR DETAILS:", str(e)) 
        return jsonify({'message': 'Database error. Check server logs.'}), 500


# NEW: get all spots for a lot (for spot modal)
# --
@admin_bp.route('/parking-lot/<int:lot_id>/spots', methods=['GET'])
def get_lot_spots(lot_id):
    """
    Note to me:
    Returns spot list for a lot. Each spot may include an active reservation blob:
    {
      id, spot_number, is_occupied,
      reservation: {
        id, user_id, user_email, start_time (ISO UTC Z), total_cost
      } | None
    }
    """
    lot = ParkingLot.query.get(lot_id)
    if not lot:
        return jsonify({'message': 'Parking lot not found'}), 404

    spots_payload = []
    for spot in lot.spots:
        active_res = (
            Reservation.query
            .filter_by(spot_id=spot.id, active=True)
            .order_by(Reservation.start_time.desc())
            .first()
        )

        res_info = None
        if active_res:
            user_email = None
            try:
                user_obj = getattr(active_res, 'user', None)
                if user_obj and getattr(user_obj, 'email', None):
                    user_email = user_obj.email
            except Exception:
                user_email = None

            # Fallback to explicit lookup if something goes wrong
            if not user_email and active_res.user_id:
                user = User.query.get(active_res.user_id)
                if user:
                    user_email = user.email

            # ISO formatting
            start_iso = None
            if active_res.start_time:
                st = active_res.start_time
                if getattr(st, 'tzinfo', None) is None:
                    st = st.replace(tzinfo=timezone.utc)
                else:
                    st = st.astimezone(timezone.utc)
                start_iso = st.isoformat().replace('+00:00', 'Z')

            res_info = {
                'id': active_res.id,
                'user_id': active_res.user_id,
                'user_email': user_email or None,
                'start_time': start_iso,
                'total_cost': float(active_res.total_cost or 0.0)
            }

        spots_payload.append({
            'id': spot.id,
            'lot_id': lot.id,
            'spot_number': spot.spot_number,
            'is_occupied': spot.is_occupied,
            'reservation': res_info
        })

    return jsonify(spots_payload), 200


# --
# NEW: release a single occupied spot (no delete)
# --
@admin_bp.route('/parking-spot/<int:spot_id>/release', methods=['POST'])
def release_parking_spot(spot_id):
    spot = ParkingSpot.query.get(spot_id)
    if not spot:
        return jsonify({'message': 'Parking spot not found'}), 404

    active_res = Reservation.query.filter_by(spot_id=spot.id, active=True).first()
    if not active_res:
        return jsonify({'message': 'Spot is not currently occupied.'}), 400

    try:
        total_cost = _close_and_bill_reservation(active_res)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to release reservation', 'error': str(e)}), 500

    cache.delete('available_lots')
    cache.delete('admin_analytics')

    return jsonify({
        'message': 'Spot released successfully.',
        'spot_id': spot.id,
        'reservation_id': active_res.id,
        'total_cost': total_cost
    }), 200


# Users list (simple)
# --
@admin_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    output = []
    for user in users:
        role = user.roles[0].name if user.roles else 'user'
        output.append({
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'role': role
        })
    return jsonify(output), 200


# --
# Analytics (global)
# --
@admin_bp.route('/analytics', methods=['GET'])
@cache.cached(timeout=300, key_prefix='admin_analytics')
def get_analytics():
    archive_name = "Deleted - Archived History"

    # Calculate Occupancy (EXCLUDING Archive)
    # We join ParkingSpot with ParkingLot to check the name
    total_spots = ParkingSpot.query.join(ParkingLot).filter(
        ParkingLot.name != archive_name
    ).count()

    occupied_spots = ParkingSpot.query.join(ParkingLot).filter(
        ParkingLot.name != archive_name,
        ParkingSpot.is_occupied == True
    ).count()
    
    occupancy_data = {
        'total': total_spots,
        'occupied': occupied_spots,
        'available': max(0, total_spots - occupied_spots),
        'occupancy_rate': round((occupied_spots / total_spots) * 100, 1) if total_spots else 0
    }

    # Calculate Total Revenue (INCLUDING Archive)
    total_revenue = db.session.query(db.func.sum(Reservation.total_cost)).scalar()
    total_revenue = round(total_revenue or 0.0, 2)

    # Sorting done
    lots = ParkingLot.query.all()
    sorted_lots = sorted(lots, key=lambda x: (1 if x.name == archive_name else 0, x.id))

    lots_summary = []
    for lot in sorted_lots:
        is_archive = (lot.name == archive_name)
        
        capacity = lot.capacity or 0
        occupied = ParkingSpot.query.filter_by(lot_id=lot.id, is_occupied=True).count()
        
        lot_rev = db.session.query(db.func.sum(Reservation.total_cost)) \
            .join(ParkingSpot, Reservation.spot_id == ParkingSpot.id) \
            .filter(ParkingSpot.lot_id == lot.id) \
            .scalar() or 0.0
            
        lots_summary.append({
            'id': lot.id,
            'name': lot.name,
            'is_archive': is_archive, # Flag for frontend
            'capacity': capacity,
            'occupied': occupied,
            'available': max(0, capacity - occupied) if not is_archive else 0,
            'total_revenue': round(float(lot_rev), 2)
        })

    return jsonify({
        'occupancy_summary': occupancy_data,
        'revenue_summary': {'total_revenue': total_revenue},
        'lots_summary': lots_summary
    }), 200


# each lot analytics endpoints
# ---
@admin_bp.route('/parking-lot/<int:lot_id>/analytics', methods=['GET'])
def get_parking_lot_analytics(lot_id):
    """
    Returns analytics for a single parking lot:
    - 30-day revenue timeseries (daily)
    - total revenue for the lot
    - today's bookings count
    - this month's bookings count
    - capacity, occupied, occupancy_rate, avg_duration_minutes
    """
    lot = ParkingLot.query.get(lot_id)
    if not lot:
        return jsonify({'message': 'Parking lot not found'}), 404
    
    # Basic counts
    capacity = lot.capacity or 0
    occupied = ParkingSpot.query.filter_by(lot_id=lot.id, is_occupied=True).count()
    occupancy_rate = round((occupied / capacity) * 100, 1) if capacity else 0

    # Total revenue for this lot (sum of all reservations' total_cost for spots in this lot)
    total_revenue = db.session.query(db.func.sum(Reservation.total_cost)) \
        .join(ParkingSpot, Reservation.spot_id == ParkingSpot.id) \
        .filter(ParkingSpot.lot_id == lot.id) \
        .scalar() or 0.0
    total_revenue = round(float(total_revenue), 2)

    # Today's / month's bookings (count of reservations that started today / this month)
    today_utc = datetime.now(timezone.utc).date()
    start_of_today = datetime(today_utc.year, today_utc.month, today_utc.day, tzinfo=timezone.utc)
    start_of_month = datetime(today_utc.year, today_utc.month, 1, tzinfo=timezone.utc)

    todays_bookings = db.session.query(db.func.count(Reservation.id)) \
        .join(ParkingSpot, Reservation.spot_id == ParkingSpot.id) \
        .filter(
            ParkingSpot.lot_id == lot.id,
            Reservation.start_time >= start_of_today
        ).scalar() or 0

    months_bookings = db.session.query(db.func.count(Reservation.id)) \
        .join(ParkingSpot, Reservation.spot_id == ParkingSpot.id) \
        .filter(
            ParkingSpot.lot_id == lot.id,
            Reservation.start_time >= start_of_month
        ).scalar() or 0

    # Average duration (for closed reservations) in minutes
    closed_res = db.session.query(Reservation) \
        .join(ParkingSpot, Reservation.spot_id == ParkingSpot.id) \
        .filter(
            ParkingSpot.lot_id == lot.id,
            Reservation.active.is_(False),
            Reservation.end_time.isnot(None),
            Reservation.start_time.isnot(None)
        ).all()

    avg_duration_minutes = 0.0
    if closed_res:
        total_minutes = 0.0
        count_closed = 0
        for r in closed_res:
            try:
                st = r.start_time
                et = r.end_time
                if getattr(st, 'tzinfo', None) is None:
                    st = st.replace(tzinfo=timezone.utc)
                else:
                    st = st.astimezone(timezone.utc)
                if getattr(et, 'tzinfo', None) is None:
                    et = et.replace(tzinfo=timezone.utc)
                else:
                    et = et.astimezone(timezone.utc)

                dur = (et - st).total_seconds() / 60.0
                if dur > 0:
                    total_minutes += dur
                    count_closed += 1
            except Exception:
                continue
        if count_closed:
            avg_duration_minutes = round(total_minutes / count_closed, 1)

    # Build 30-day revenue timeseries (date -> revenue)
    timeseries = []
    days = 30
    for offset in range(days - 1, -1, -1):  # oldest -> newest
        day_date = today_utc - timedelta(days=offset)
        day_start = datetime(day_date.year, day_date.month, day_date.day, tzinfo=timezone.utc)
        day_end = day_start + timedelta(days=1)

        day_total = db.session.query(db.func.sum(Reservation.total_cost)) \
            .join(ParkingSpot, Reservation.spot_id == ParkingSpot.id) \
            .filter(
                ParkingSpot.lot_id == lot.id,
                Reservation.start_time >= day_start,
                Reservation.start_time < day_end,
                Reservation.total_cost.isnot(None)
            ).scalar() or 0.0

        timeseries.append({
            'date': day_start.date().isoformat(),
            'revenue': round(float(day_total), 2)
        })

    resp = {
        'lot_id': lot.id,
        'lot_name': lot.name,
        'capacity': capacity,
        'occupied': occupied,
        'occupancy_rate': occupancy_rate,
        'total_revenue': total_revenue,
        'timeseries_30d': timeseries,
        'todays_bookings': int(todays_bookings),
        'months_bookings': int(months_bookings),
        'avg_duration_minutes': avg_duration_minutes
    }

    return jsonify(resp), 200


# below part added later
# Get single user details + reservation history (UTC-safe)
# --
@admin_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user_details(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    role = user.roles[0].name if user.roles else 'user'

    # If User.reservations relationship exists, use it; otherwise query.

    
    try:
        all_reservations = sorted(user.reservations, key=lambda r: r.start_time or datetime.min, reverse=True)
    except Exception:
        all_reservations = Reservation.query.filter_by(user_id=user.id).order_by(Reservation.start_time.desc()).all()

    def to_utc_iso(dt):
        """Return a UTC ISO string with trailing Z, defensively handling naive datetimes."""
        if not dt:
            return None
        if getattr(dt, 'tzinfo', None) is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return dt.isoformat().replace('+00:00', 'Z')

    reservations_data = []
    for r in all_reservations:
        start_iso = to_utc_iso(r.start_time)
        end_iso = to_utc_iso(r.end_time)

        # compute duration_seconds for frontend-friendly formatting
        if r.start_time:
            st = r.start_time
            if getattr(st, 'tzinfo', None) is None:
                st = st.replace(tzinfo=timezone.utc)
            else:
                st = st.astimezone(timezone.utc)
            if r.end_time:
                et = r.end_time
                if getattr(et, 'tzinfo', None) is None:
                    et = et.replace(tzinfo=timezone.utc)
                else:
                    et = et.astimezone(timezone.utc)
            else:
                et = datetime.now(timezone.utc)

            duration_seconds = max(0, int((et - st).total_seconds()))
        else:
            duration_seconds = 0

        reservations_data.append({
            'id': r.id,
            'lot_name': getattr(getattr(r, 'spot', None), 'parking_lot', None).name if getattr(r, 'spot', None) and getattr(r.spot, 'parking_lot', None) else None,
            'spot_number': getattr(r, 'spot', None).spot_number if getattr(r, 'spot', None) else None,
            'start_time': start_iso,
            'end_time': end_iso,
            'duration_seconds': duration_seconds,
            'active': bool(r.active),
            'total_cost': float(r.total_cost or 0.0)
        })

    return jsonify({
        'id': user.id,
        'username': getattr(user, 'username', None),
        'email': getattr(user, 'email', None),
        'role': role,
        'reservations': reservations_data
    }), 200
