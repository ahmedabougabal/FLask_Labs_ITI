from flask import Flask, render_template, url_for, redirect, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "Ahmed123"  # session key
app.permanent_session_lifetime = timedelta(days=5)  # session_lifetime

# Database configuration
# Step-1
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
db = SQLAlchemy(app)

# Step-2: Define User Schema
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=True)
    books = db.relationship('Book', backref='owner', lazy="select")  # relationship with books
    role = db.Column(db.String(10), default='user')
    # backref: how to get data from of books of this user or vise verse: (will be understood in below code)
    # lazy: how tables will get at database background (default is select) check it's types (https://docs.sqlalchemy.org/en/14/orm/loading_relationships.html)

    def __init__(self, username, password=None):
        self.username = username
        if password:
            self.password = password

# Define Book Schema
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def __init__(self, title, user_id=None):
        self.title = title
        self.user_id = user_id

# Routes
@app.route("/home")
@app.route("/")
def home_page():
    return render_template("home.html")


@app.route("/signup", methods=['GET', 'POST'])
def sign_up():
    if request.method == "POST":  # POST
        user_name = request.form['nm']
        password = request.form['ps']
        confirm_password = request.form['confirm_ps']

        if password == confirm_password:
            found_user = User.query.filter_by(username=user_name).first()
            if found_user:
                flash("User Already Exists")
                return render_template("users/signup.html")
            else:
                hashed_password = generate_password_hash(password)
                u1 = User(user_name, hashed_password)
                db.session.add(u1)
                db.session.commit()
                return redirect(url_for("login"))
        else:
            flash("Password and confirm password don't match")
            return render_template("users/signup.html")
    else:  # GET
        return render_template("users/signup.html")


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        if 'username' in session.keys():
            flash("Already Logged In", "info")
            return redirect(url_for('user_profile'))
        else:
            return render_template("login.html", images=['images_3.png', 'images_4.png'])
    else:  # POST
        user_name = request.form['nm']
        password = request.form['ps']
        user_found = User.query.filter_by(username=user_name).first()

        if user_found and check_password_hash(user_found.password, password):
            session['username'] = user_name
            session['password'] = user_found.password
            session.permanent = True
            flash("Successfully logged in", "info")
            return redirect(url_for('user_profile'))
        else:
            flash("Incorrect credentials", 'info')
            return redirect(url_for("sign_up"))


@app.route("/profile", endpoint='user_profile')
def show_profile():
    if 'username' in session.keys():
        name = session['username']
        password = session['password']
        return render_template("profile.html", name=name, password=password)
    else:
        flash("Session ended, please login again", "info")
        return redirect(url_for("login"))


@app.route("/logout")
def logout():
    session.pop('username', None)
    session.pop('password', None)
    return redirect(url_for("home_page"))


@app.route("/edit", methods=['GET', 'POST'])
def edit():
    if 'username' not in session:
        flash("You must be logged in to edit your username", "error")
        return redirect(url_for('login'))

    if request.method == 'POST':
        new_username = request.form['username']
        user = User.query.filter_by(username=session['username']).first()
        if user:
            user.username = new_username
            db.session.commit()
            session.pop('username')
            flash("Username edited successfully, please login with your new username", "success")
            return redirect(url_for('login'))
        else:
            flash("User not found", "error")
    return render_template('edit.html')


@app.route("/delete", methods=['GET', 'POST'])
def delete():
    if 'username' not in session:
        flash("You must be logged in to delete your account", "error")
        return redirect(url_for('login'))

    user = User.query.filter_by(username=session['username']).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        session.pop('username')
        flash("Account deleted successfully", "success")
        return redirect(url_for('sign_up'))
    else:
        flash("User not found", "error")
        return redirect(url_for('show_profile'))


@app.route("/admin/dashboard", methods=['GET'])
def admin_dashboard():
    if 'username' not in session or session.get('role') != 'admin':
        flash("Access denied. Admins only.", "error")
        return redirect(url_for("home_page"))

    users = User.query.all()  # Fetch all users
    books = Book.query.all()  # Fetch all books
    return render_template("admin_dashboard.html", users=users, books=books)


@app.route("/book/add", methods=['GET', 'POST'])
def add_book():
    if 'username' not in session:
        flash("Please login to add books.", "error")
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        book_title = request.form['title']
        if book_title:
            user = User.query.filter_by(username=session['username']).first()
            new_book = Book(title=book_title, user_id=user.id)
            db.session.add(new_book)
            db.session.commit()
            flash("Book added successfully!", "success")
            return redirect(url_for("user_profile"))
        else:
            flash("Book title cannot be empty.", "error")

    return render_template("add_book.html")


@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/error.html'), 404


@app.route("/")
def run_all():
    ## Step-3
    # Create a new user
    new_user = User(username='Ahmed Ayman')
    db.session.add(new_user)
    db.session.commit()
    print("Added User")

    # Add a book
    new_book = Book(title='Flask Book')  # could specfiy also user_id=5 or owner=new_user
    # new_book = Book(title='Flask Book', user_id=new_user.id)
    db.session.add(new_book)
    db.session.commit()
    print("Added Book")


    # [Add a book for user]
    user = User.query.get(new_user.id)
    book = Book.query.get(new_book.id)
    if user and book:
        book.user_id = user.id # add fk then submit
        db.session.commit()

    # what is backref? (to get books of a user without multible queries and vice versa)
    user = User.query.filter_by(username='Ahmed Ayman2').first()  # when getting user I can get his books also vise-verse(Book.owser.username)
    books = user.books  # don't worry it's not error, it gets books of user

    for book in books:
        print(book.title)
        print(book.owner.username)  # and username of a book

    return "Congratulations, Data Processed Successfully!"

# Database creation
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
