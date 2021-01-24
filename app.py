from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import hashlib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, unique=True, nullable = False)
    password = db.Column(db.String, unique=True, nullable = False)

class Logged(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, unique=True, nullable = False)

@app.route("/")
def main():
    return render_template("home.html")

@app.route("/logged")
def logged_page():
    user = Logged.query.order_by(Logged.id.desc()).first()
    return render_template("logged.html", profile=user.username)

@app.route("/signin", methods=['GET', 'POST'])
def log_page():
    if request.method == 'GET':
        return render_template("login.html")
    else:
        username = request.form['username']
        password = (request.form['password'])
        password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        user = User.query.filter_by(username = username, password = password).first()
        if user is None:
            return render_template("login.html", mesage="Try agai! This profile is not exists!")
        else:
            logged = Logged(username=username)
            db.session.add(logged)
            return redirect('/logged')

    

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
            logged = Logged(username=username)
            db.session.add(logged)
            db.session.commit()
            return redirect('/logged')
        else:
            return render_template("registration.html", mesage="Try agai! This username is already used!")

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)