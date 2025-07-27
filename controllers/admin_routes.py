from flask import render_template, request, redirect, url_for , session
from models.model import db, ParkingLot, ParkingSpot, User, Reservation
from sqlalchemy.sql import func

def setup_admin_routes(app):

    @app.route("/admin")
    def admin_dashboard():
        lots = ParkingLot.query.all()
        return render_template('admin_dashboard.html', lots=lots)

    @app.route("/admin/lots")
    def list_lots():
        lots = ParkingLot.query.all()
        return render_template("lot_list.html", lots=lots)

    @app.route("/admin/lots/create", methods=["GET", "POST"])
    def create_lot():
        if request.method == "POST":
            name = request.form["name"]
            price = float(request.form["price"])
            address = request.form["address"]
            pin = request.form["pin"]
            capacity = int(request.form["capacity"])

            lot = ParkingLot(prime_location_name=name, price_per_hour=price, address=address, pin_code=pin, maximum_number_of_spots=capacity)
            db.session.add(lot)
            db.session.commit()

            for _ in range(capacity):
                spot = ParkingSpot(lot_id=lot.id, status='A')
                db.session.add(spot)
            db.session.commit()

            return redirect(url_for('admin_dashboard'))

        return render_template("lot_form.html")

    @app.route("/admin/lots/<int:lot_id>/spots")
    def view_spots(lot_id):
        lot = ParkingLot.query.get_or_404(lot_id)
        return render_template("spot_list.html", lot=lot)

    @app.route("/admin/lots/delete/<int:lot_id>")
    def delete_lot(lot_id):
        lot = ParkingLot.query.get_or_404(lot_id)
        db.session.delete(lot)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    
    @app.route("/admin/users")
    def list_users():
        users = User.query.all()
        return render_template("user_list.html", users=users)

    @app.route("/admin/search", methods=["GET", "POST"])
    def search():
        lots = []
        if request.method == "POST":
            category = request.form["category"]
            query = request.form["search_query"]

            if category == "user":
                user = User.query.filter_by(id=query).first()
                if user:
                    reservations = Reservation.query.filter_by(user_id=user.id).all()
                    lots = [res.spot.lot for res in reservations if res.spot and res.spot.lot]

            elif category == "location":
                lots = ParkingLot.query.filter(ParkingLot.prime_location_name.ilike(f"%{query}%")).all()

        return render_template("search.html", lots=lots)
    @app.route("/admin/spot/<int:spot_id>")
    def view_spot(spot_id):
        spot = ParkingSpot.query.get_or_404(spot_id)
        return render_template("spot_view.html", spot=spot)

    @app.route("/admin/spot/<int:spot_id>/details")
    def view_occupied_spot(spot_id):
        spot = ParkingSpot.query.get_or_404(spot_id)
        reservation = Reservation.query.filter_by(spot_id=spot.id).order_by(Reservation.parking_timestamp.desc()).first()
        return render_template("occupied_spot_details.html", spot=spot, reservation=reservation)

    @app.route("/admin/spot/<int:spot_id>/delete")
    def delete_spot(spot_id):
        spot = ParkingSpot.query.get_or_404(spot_id)
        if spot.status == 'R':
            return "Cannot delete an occupied spot."
        db.session.delete(spot)
        db.session.commit()
        return redirect(f"/admin/lots/{spot.lot_id}/spots")

    @app.route("/admin/reservations")
    def all_reservations():
        reservations = Reservation.query.order_by(Reservation.parking_timestamp.desc()).all()
        return render_template("all_reservations.html", reservations=reservations)
    @app.route("/admin/summary")
    def admin_summary():
        if session.get("role") != "admin":
            return redirect("/login")
        
        revenue_data = db.session.query(
            ParkingLot.prime_location_name,
            func.sum(Reservation.parking_cost)
        ).select_from(Reservation) \
         .join(ParkingSpot, Reservation.spot_id == ParkingSpot.id) \
         .join(ParkingLot, ParkingSpot.lot_id == ParkingLot.id) \
         .group_by(ParkingLot.prime_location_name) \
         .all()

        spot_data = []
        lots = ParkingLot.query.all()
        for lot in lots:
            total = lot.maximum_number_of_spots
            occupied = sum(1 for spot in lot.spots if spot.status == 'R')
            available = total - occupied
            spot_data.append({
                "lot": lot.prime_location_name,
                "occupied": occupied,
                "available": available
            })

        return render_template("admin_summary.html", revenue_data=revenue_data, spot_data=spot_data)