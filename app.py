from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import hashlib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, nullable = False)
    password = db.Column(db.String, nullable = False)
@app.route("/")
def main():
    return render_template("home.html")

@app.route("/logged")
def logged_page():
    return render_template("logged.html")

@app.route("/signin")
def log_page():
    return render_template("login.html")

@app.route("/signup", methods=['GET', 'POST'])
def reg_page():
    if request.method == 'GET':
        return render_template("registration.html")
    else:
        username = request.form['username']
        user = User.query.filter_by(username = username).first()
        if user is None:
            password = (request.form['password'])
            password = hashlib.sha256(password.encode('utf-8')).hexdigest()
            record = User(username=username, password=password)
            db.session.add(record)
            db.session.commit()
            return render_template("logged.html", profile=username)
        else:
            return render_template("registration.html", mesage="Try agai! This username is already used!")

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)