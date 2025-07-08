from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models.model import db
from controllers.user_routes import setup_user_routes
from controllers.admin_routes import setup_admin_routes
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///parking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False    
db.init_app(app)

setup_user_routes(app)
setup_admin_routes(app)

if __name__ == "__main__":
    with app.app_context():
        db.create_all() 
    app.run(debug=True)  
