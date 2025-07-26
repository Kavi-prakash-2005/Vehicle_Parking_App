from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models.model import db , Admin 
from controllers.user_routes import setup_user_routes
from controllers.admin_routes import setup_admin_routes
from controllers.setup_api_routes import setup_api_routes

app = Flask(__name__)
app.secret_key = 'Kp-admin@1234'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False    
db.init_app(app)

setup_user_routes(app)
setup_admin_routes(app)
setup_api_routes(app)
if __name__ == "__main__":
    with app.app_context():
        db.create_all() 

        if not Admin.query.filter_by(username="admin").first():
            admin = Admin(username="admin", password="admin123")
            db.session.add(admin)
            db.session.commit()
        
    app.run(debug=True)  
