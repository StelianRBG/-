from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
import hashlib
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from datetime import datetime


#app configoration
app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissecret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)


#login_manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


#user 
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), nullable = False)
    password = db.Column(db.String(32), nullable = False)


#category
class Topic(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50), nullable = False)
    description = db.Column(db.String(200), nullable = False)
    user = db.Column(db.String(20), nullable = False)
    timestamp = db.Column(db.DateTime, nullable = False, default = datetime.now())


#post
class Post(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	heading = db.Column(db.String, nullable = False)
	content = db.Column(db.String, nullable = False)
	topic = db.Column(db.Integer, nullable = True)
	user = db.Column(db.String, nullable = True)
	timestamp = db.Column(db.DateTime, nullable = False, default = datetime.now())


#login_manager
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


#home page
@app.route('/')
def main():
	logout_user()
	return render_template('home.html', topics = Topic.query.all())


#logged page
@app.route('/logged', methods=['GET', 'POST'])
@login_required
def logged_page():
	if request.method == 'GET':
		return render_template('logged.html', profile = current_user.username, topics = Topic.query.all())
	else:
		name = request.form['name']
		desc = request.form['desc']
		record = Topic(name = name, description = desc, user = current_user.username)

		db.session.add(record)
		db.session.commit()
		return redirect('/logged')


#signin page
@app.route('/signin', methods=['GET', 'POST'])
def log_page():
	if request.method == 'GET':
		return render_template('login.html')
	else:
		username = request.form['username']
		password = request.form['password']
		
		password = hashlib.sha256(password.encode('utf-8')).hexdigest()
		user = User.query.filter_by(username = username, password = password).first()

		if not user:
			flash('Try again! Wrong username or password')
			return redirect('/signin')
		else:
			login_user(user)
			return redirect('/logged')


#signup page
@app.route('/signup', methods=['GET', 'POST'])
def reg_page():
	if request.method == 'GET':
		return render_template('registration.html')
	else:
		username = request.form['username']
		if len(username) > 20:
			flash('Password must not be more than 20 characters long!')
			return redirect('/signup')

		user = User.query.filter_by(username = username).first()

		if not user:
			password = request.form['password']
			confirm = request.form['confirm']
			
			if password != confirm:
				flash('Try again! Password has not been confirmed!')
				return redirect('/signup')
			if len(password) < 8:
				flash('Try again! Password must be 8 characters at least!')
				return redirect('/signup')
			if len(password) > 32:
				flash('Try again! Password must be 32 characters at most!')
				return redirect('/signup')
			
			password = hashlib.sha256(password.encode('utf-8')).hexdigest()
			record = User(username=username, password=password)
			
			db.session.add(record)
			db.session.commit()
			
			login_user(record)
			flash('You have been successfully registered')
			return redirect('/logged')
		else:
			flash('Try again! This username has already been taken!')
			return redirect('/signup')


#outside user sees posts (can't make post)
@app.route('/see/<int:id>')
def see_posts(id):
	topic = Topic.query.filter_by(id = id).first()
	return render_template('posts.html', topic = topic, posts = Post.query.filter_by(topic = id).all())


#logged user sees posts (can make post)
@app.route('/topic/<int:id>', methods=['GET', 'POST'])
@login_required
def list_posts(id):
	if request.method == 'GET':
		topic = Topic.query.filter_by(id = id).first()
		return render_template('loggedposts.html', topic = topic, posts = Post.query.filter_by(topic = id).all())
	else:
		header = request.form['name']
		content = request.form['content']
		record = Post(heading = header, content = content, topic = id, user = current_user.username)
		db.session.add(record)
		db.session.commit()

		topic = Topic.query.filter_by(id = id).first()
		return redirect(url_for('list_posts', id = topic.id))


#update post page
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
	post = Post.query.filter_by(id = id).first()
	red = post.topic

	if request.method == 'GET':
		return render_template('update.html', post = post)
	else:
		post.heading = request.form['new_name']
		post.content = request.form['new_content']
		db.session.commit()
		return redirect(url_for('list_posts', id = red))


#delete post
@app.route('/delete/<int:id>')
@login_required
def delete(id):
	obj = Post.query.filter_by(id = id).first()
	red = obj.topic

	db.session.delete(obj)
	db.session.commit()

	return redirect(url_for('list_posts', id = red))


#main
if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)