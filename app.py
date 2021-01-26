from flask import Flask, render_template, request, redirect, flash 
from flask_sqlalchemy import SQLAlchemy
import hashlib
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, nullable = False)
    password = db.Column(db.String, nullable = False)

class Category(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(30), nullable = False)
	
	
class Post(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	heading = db.Column(db.String(100), nullable = False)
	content = db.Column(db.String(500), nullable = False)
	user = db.Column(db.String, nullable = True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def main():
    logout_user()
    return render_template("home.html")

@app.route("/logged")
def logged_page():
    return render_template("logged.html", profile = current_user.username)

@app.route("/signin", methods=['GET', 'POST'])
def log_page():
    if request.method == 'GET':
        return render_template("login.html")
    else:
        username = request.form['username']
        password = request.form['password']
        password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        user = User.query.filter_by(username = username, password = password).first()
        if not user:
            flash("Try agai! Wrong username or password")
            return redirect("/signin")
        else:
            login_user(user)
            return redirect('/logged')

    

@app.route("/signup", methods=['GET', 'POST'])
def reg_page():
    if request.method == 'GET':
        return render_template("registration.html")
    else:
        username = request.form['username']
        user = User.query.filter_by(username = username).first()
        if not user:
            password = request.form['password']
            confirm = request.form['confirm']
            if password != confirm:
                flash("Try agai! Password is not confirmed!")
                return redirect('/signup')
            password = hashlib.sha256(password.encode('utf-8')).hexdigest()
            record = User(username=username, password=password)
            db.session.add(record)
            db.session.commit()
            flash('You were successfully registrate')
            return redirect('/signin')
        else:
            flash('Try agai! This username is already used!')
            return redirect('/signup')


# nov post 
@app.route('/posts/new', methods = ['GET', 'POST'])
def new_post():
	if request.method == 'GET':
		return render_template('newpost.html')
	elif request.method == 'POST':
		header = request.form['name']
		content = request.form['content']
		record = Post(heading = header, content = content, user = "hmm")
		db.session.add(record)
		db.session.commit()
		return redirect('/')
	
# nov komentar
@app.route('/cat/new', methods = ['GET', 'POST'])
def new_cat():
	if request.method == 'GET':
		return render_template('newcat.html')
	elif request.method == 'POST':
		name = request.form["name"]
		category = Category(name = name)
		db.session.add(category)
		db.session.commit()
		return redirect("/")


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)