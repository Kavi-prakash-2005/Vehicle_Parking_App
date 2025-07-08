from flask import render_template

def setup_admin_routes(app):
    # Admin Dashboard
    @app.route("/admin")
    def admin_dashboard():
        return "Admin Dashboard"
