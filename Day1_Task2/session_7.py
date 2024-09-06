from flask import Flask, render_template, url_for, redirect
from flask import request, session # routing data through pages without calling db everytime
from flask import flash
from datetime import timedelta

## message flashing
app = Flask(__name__)
app.secret_key = "Ahmed123" # session key
app.permanent_session_lifetime = timedelta(days=5) # session_lifetime
# app['SERCRET_KEY'] = ""

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
    if request.method == "POST": # POST
        user_name = request.form['nm']
        password = request.form['ps']
        confirm_password = request.form['confirm_ps']
        # validate confirm == password
        if password == confirm_password:
            # validate db
            return f"Username is {user_name}, Password is {password}"
        else:
            return f"confirm password and password doesnt match"
    else: # GET
        
        return render_template("users/signup.html") # users/signup.html

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "GET": # GET
        if 'username' in session.keys():
            flash("Already logged in", "info")
            return redirect(url_for('user.profile'))
        else:
            flash("Please Type username and password", "info")
            return render_template("login.html", images=['images_3.png', 'images_4.png'])
    else: # POST
        user_name = request.form['nm']
        password = request.form['ps']
        # validate db
        session['username'] = user_name
        session['password'] = password
        session.permanent = True # to reopen borwser and session is saved their
        flash("Successfully login", "info")
        return redirect(url_for('user.profile'))

@app.route('/logout')
def logout():
    if("username" in session):
        session.pop('username')
    if("password" in session): 
        session.pop('password')
    flash("successfully logged out", "info")
    return redirect(url_for('login')) 



@app.route("/profile", endpoint='user.profile')
def show_profile():
    if 'username' in session.keys():
        name = session['username']
        password = session['password']
        return render_template("profile.html", name=name, password=password)
    else: # session ends
        flash("Sessions ends, please rewrite username and password", "info")
        return redirect(url_for("login"))
   

if __name__ == "__main__":
    print(app.url_map)
    app.run(debug=True, port=5000)