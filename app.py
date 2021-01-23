from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

@app.route("/")
def main():
    return render_template("home.html")

@app.route("/signin")
def log_page():
    return render_template("login.html")

@app.route("/signup")
def reg_page():
    return render_template("registration.html")

if __name__ == "__main__":
    app.run(debug=True)