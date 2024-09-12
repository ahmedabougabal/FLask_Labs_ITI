from flask import Blueprint, render_template, url_for, flash, redirect, request, abort
from flask_login import login_user, current_user, logout_user, login_required
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db, bcrypt
from app.models import User, Book
from app.forms import RegistrationForm, LoginForm

bp = Blueprint('main', __name__)

@bp.route("/")
@bp.route("/index")
def index():
    return render_template('index.html')

@bp.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

@bp.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route("/add_item", methods=['GET', 'POST'])
@login_required
def add_item():
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        new_book = Book(title=title, author=author, user_id=current_user.id)
        db.session.add(new_book)
        db.session.commit()
        flash('Book added successfully!', 'success')
        return redirect(url_for('main.view_items'))
    return render_template('add_item.html', title='Add Item')

@bp.route("/view_items")
@login_required
def view_items():
    books = Book.query.filter_by(user_id=current_user.id).all()
    return render_template('view_items.html', title='View Items', books=books)

@bp.route("/remove_item/<int:book_id>", methods=['POST'])
@login_required
def remove_item(book_id):
    book = Book.query.get_or_404(book_id)
    if book.user_id != current_user.id:
        abort(403)
    db.session.delete(book)
    db.session.commit()
    flash('Book removed successfully!', 'success')
    return redirect(url_for('main.view_items'))

@bp.route("/admin_dashboard")
@login_required
@jwt_required
def admin_dashboard():
    if not current_user.is_admin:
        abort(403)
    users = User.query.all()
    books = Book.query.all()
    return render_template('admin_dashboard.html', title='Admin Dashboard', users=users, books=books)

@bp.route("/delete_user/<int:user_id>", methods=['POST'])
@login_required
@jwt_required
def delete_user(user_id):
    if not current_user.is_admin:
        abort(403)
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'success')
    return redirect(url_for('main.admin_dashboard'))

@bp.route("/delete_book/<int:book_id>", methods=['POST'])
@login_required
@jwt_required
def delete_book(book_id):
    if not current_user.is_admin:
        abort(403)
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    flash('Book deleted successfully!', 'success')
    return redirect(url_for('main.admin_dashboard'))