from flask import Flask, render_template, url_for, redirect
from flask import request, session  # routing data through pages without calling db everytime
from flask import flash,app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.functions import current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

## message flashing
app = Flask(__name__)
app.secret_key = "Ahmed123"  # session key
app.permanent_session_lifetime = timedelta(days=5)  # session_lifetime

## step-1
# http://127.0.0.1:5000/students
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
db = SQLAlchemy(app)


# app['SERCRET_KEY'] = ""

## step-2
### Model
class User(db.Model):
  #  __tablename__ = "users"
  # static attributes {schema of db}
  id = db.Column('id', db.Integer, primary_key=True)
  username = db.Column(db.String(50), unique=True)
  password = db.Column(db.String(50), nullable=False)

  def __init__(self, username, password):
    self.username = username
    self.password = password


@app.route("/home")
@app.route("/")
def home_page():
  return render_template("home.html")


# def login_page():
#     return render_template("login.html")

# app.add_url_rule("/login", view_func=login_page)

## http methods [GET, POST]

@app.route("/signup", methods=['GET', 'POST'])
def sign_up():
  if request.method == "POST":  # POST
    user_name = request.form['nm']
    password = request.form['ps']
    confirm_password = request.form['confirm_ps']
    # validate confirm == password
    if password == confirm_password:
      # validate db
      found_user = User.query.filter_by(username=user_name).first()  # if found User, else None
      if found_user:  # already exists b4
        flash("User Already Exists")
        return render_template("users/signup.html")
      else:  # save account
        hashed_password = generate_password_hash(password)
        u1 = User(user_name, hashed_password)
        db.session.add(u1)
        db.session.commit()

        # db.session.delete(u1)
        # db.session.commit()

        # u1.username = 'Ziad'
        # db.session.commit()

        # User.query.filter_by(username='Ahmed') # equality only
        # User.query.filter(User.username) # where

        # SELECT, FROM, WHERE, GROUP_BY, HAVING, ORDER_BY, LIMIT
        # from sqlalchemy import func, and_, or_, not_
        # users_result = User.query.with_entities(User.username, func.count(User.id)).filter(User.id > 0).group_by(User.username).having(func.count(User.id) >= 1).order_by(func.count(User.id).desc()).limit(3).all()
        # # users_result = User.query.with_entities(User.id, func.count(User.username)).filter(and_(User.id > 0, User.username=='Ahmed')).group_by(User.id).having(func.count(User.username) >= 1).order_by(func.count(User.username).desc()).limit(3).all()
        # print(users_result)
        return redirect(url_for("login"))

    else:
      flash("confirm password and password doesnt match")
      return render_template("users/signup.html")
  else:  # GET
    return render_template("users/signup.html")  # users/signup.html


@app.route("/login", methods=['GET', 'POST'])
def login():
  if request.method == "GET":  # GET
    if 'username' in session.keys():
      flash("Already Logined", "info")
      return redirect(url_for('user.profile'))
    else:
      flash("Please Type username and password", "info")
      return render_template("login.html", images=['images_3.png', 'images_4.png'])
  else:  # POST
    user_name = request.form['nm']
    password = request.form['ps']
    # vliadate db
    user_found = User.query.filter_by(username=user_name).first()  # if not None
    if user_found:
      if check_password_hash(user_found.password, password):
        # session
        session['username'] = user_name
        session['password'] = user_found.password
        session.permanent = True  # to reopen borwser and session is saved their
        flash("Successfully login", "info")
        return redirect(url_for('user.profile'))
      else:
        flash("Incorrect Password", 'info')
        return render_template("login.html")
    else:
      flash("Account Doesn't Exist", 'info')
      return redirect(url_for("sign_up"))


@app.route("/profile", endpoint='user.profile')
def show_profile():
  if 'username' in session.keys():
    name = session['username']
    password = session['password']
    return render_template("profile.html", name=name, password=password)
  else:  # session ends
    flash("Sessions ends, please rewrite username and password", "info")
    return redirect(url_for("login"))


@app.route("/logout")
def logout():
  if 'username' in session.keys():
    session.pop('username')
    session.pop('password')
  return redirect(url_for("home_page"))


# route for edit button
# must be logged in to edit your username
@app.route("/edit", methods=['GET', 'POST'])
def edit():
    if 'username' not in session:
        flash("You are not allowed to edit your username", "error")
        return redirect(url_for('login'))

    if request.method == 'POST':
        new_username = request.form['username']
        user = User.query.filter_by(username=session['username']).first()
        if user:
            user.username = new_username
            db.session.commit()
            session.pop('username')
            flash("You are now edited successfully, now to login with your new username", "success")
            return redirect(url_for('login'))
        else:
            flash("User not found", "error")

    return render_template('edit.html')

@app.route("/delete", methods=['GET', 'POST'])
def delete():
    if 'username' not in session:
        flash("You are not allowed to delete your account, must be logged in first", "error")
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session['username']).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        session.pop('username')
        flash("You are now deleted successfully, create a new account if you wish", "success")
        return redirect(url_for('sign_up'))
    else:
        flash("User not found", "error")
        return redirect(url_for('show_profile'))

@app.errorhandler(404)
def error(error):
    return render_template('errors/error.html')

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
