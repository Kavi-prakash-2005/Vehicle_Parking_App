from flask import jsonify
from models.model import ParkingLot, ParkingSpot, Reservation

def setup_api_routes(app):
    
    @app.route("/api/lots", methods=["GET"])
    def api_get_lots():
        lots = ParkingLot.query.all()
        return jsonify([
            {
                "id": lot.id,
                "name": lot.prime_location_name,
                "address": lot.address,
                "pin_code": lot.pin_code,
                "price_per_hour": lot.price_per_hour,
                "spots": lot.maximum_number_of_spots
            }
            for lot in lots
        ])

    @app.route("/api/spots", methods=["GET"])
    def api_get_spots():
        spots = ParkingSpot.query.all()
        return jsonify([
            {
                "id": s.id,
                "lot_id": s.lot_id,
                "status": s.status
            }
            for s in spots
        ])

    @app.route("/api/reservations", methods=["GET"])
    def api_get_reservations():
        reservations = Reservation.query.all()
        return jsonify([
            {
                "id": r.id,
                "user_id": r.user_id,
                "spot_id": r.spot_id,
                "lot_name": r.spot.lot.prime_location_name,
                "start": r.parking_timestamp,
                "end": r.leaving_timestamp,
                "cost": r.parking_cost
            }
            for r in reservations
        ])
