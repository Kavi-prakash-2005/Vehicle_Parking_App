from flask import render_template, request, redirect, session, url_for
from models.model import User, Admin, ParkingLot, ParkingSpot ,Reservation ,db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.sql import func

def setup_user_routes(app):

    @app.route("/")
    def home():
        return render_template("home.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form["username"]
            email = request.form["email"]
            user_password = (request.form["password"])
            address = request.form["address"]
            pin_code = request.form["pin_code"]
            if not username or not email or not user_password or not address or not pin_code:
                return "All fields are required", 400

            if len(user_password) < 6:
                return "Password must be at least 6 characters", 400

            if not pin_code.isdigit() or len(pin_code) != 6:
                return "Pin code must be a 6-digit number", 400

            if User.query.filter_by(username=username).first():
                return "Username already exists", 400

            # Passed validation → hash password and save
            password = generate_password_hash(user_password)
            user = User(username=username,  password=password, email=email, address=address, pin_code=pin_code)
            db.session.add(user)
            db.session.commit()
            return redirect("/login")

        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            if not username or not password:
                return "Username and password required", 400

            if username == "admin":
                admin = Admin.query.filter_by(username="admin").first()
                if admin and admin.password == password:
                    session["role"] = "admin"
                    return redirect("/admin")
            else:
                user = User.query.filter_by(username=username).first()
                if user and check_password_hash(user.password, password):
                    session["role"] = "user"
                    session["user_id"] = user.id
                    return redirect("/user/dashboard")

            return "Invalid credentials"

        return render_template("login.html")

    @app.route("/user/dashboard")
    def user_dashboard():
        user_id = session.get("user_id")
        reservations = Reservation.query.filter_by(user_id=user_id).order_by(Reservation.parking_timestamp.desc()).all()
        return render_template("user_dashboard.html", reservations=reservations)

    
    @app.route("/user/search", methods=["GET", "POST"])
    def user_search():
        lots = []
        if request.method == "POST":
            query = request.form["search"]
            lots = ParkingLot.query.filter(
                (ParkingLot.prime_location_name.ilike(f"%{query}%")) |
                (ParkingLot.pin_code.ilike(f"%{query}%"))
            ).all()
        return render_template("user_search.html", lots=lots)
    
    @app.route("/user/book/<int:lot_id>", methods=["GET", "POST"])
    def book_parking(lot_id):
        user_id = session.get("user_id")
        lot = ParkingLot.query.get_or_404(lot_id)
        spot = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').first()

        if not spot:
            return "No available spots in this lot."

        if request.method == "POST":
            vehicle_no = request.form["vehicle_no"]
            spot.status = 'R'
            res = Reservation(
                user_id=user_id,
                spot_id=spot.id,
                parking_timestamp=datetime.now(),
                parking_cost=lot.price_per_hour,  
            )
            db.session.add(res)
            db.session.commit()
            return redirect("/user/dashboard")

        return render_template("book_spot.html", lot=lot, spot=spot, user_id=user_id)
    @app.route("/user/release/<int:reservation_id>", methods=["GET", "POST"])
    def release_parking(reservation_id):
        res = Reservation.query.get_or_404(reservation_id)
        spot = res.spot
        if request.method == "POST":
            res.leaving_timestamp = datetime.now()
            duration = (res.leaving_timestamp - res.parking_timestamp).total_seconds() / 3600
            rate = spot.lot.price_per_hour
            res.parking_cost = round(duration * rate, 2)
            spot.status = 'A'
            db.session.commit()
            return redirect("/user/dashboard")

        return render_template("release_spot.html", res=res, spot=spot)
    
    @app.route("/user/summary")
    def user_summary():
        if "user_id" not in session:
            return redirect("/login")

        user_id = session.get("user_id")

        usage = db.session.query(
            ParkingLot.prime_location_name,
            func.count(Reservation.id)
        ).select_from(Reservation) \
         .join(ParkingSpot, Reservation.spot_id == ParkingSpot.id) \
         .join(ParkingLot, ParkingSpot.lot_id == ParkingLot.id) \
         .filter(Reservation.user_id == user_id) \
         .group_by(ParkingLot.prime_location_name) \
         .all()

        return render_template("user_summary.html", usage=usage)


