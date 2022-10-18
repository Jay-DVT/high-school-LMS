from re import A
from flask import Blueprint, render_template, redirect, request, url_for, session

auth = Blueprint('auth', __name__)

#methods=['GET', 'POST'] is a decorator
@auth.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        print(data)
    return render_template("login.html")

@auth.route('/logout')
def logout():
    return "<p>Logout</p>"

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template("signup.html")

    # session["name"] = None
    # return redirect('/')



# if logged in, redirect to index
#     if request.method == "POST":
#         session["name"] = request.form.get("name")
#         return redirect ("/")
#     return render_template('login.html')