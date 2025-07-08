from flask import render_template, request, redirect

def setup_user_routes(app):
    # User 
    @app.route("/register", methods=["GET", "POST"])
    def register():
        return "User Registration Page"

    # login
    @app.route("/login", methods=["GET", "POST"])
    def login():
        return "Admin Registration Page"
