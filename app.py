from flask import Flask, session, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_session import Session

#app config
app = Flask(__name__)
#session config
# Secret key with imported value
app.config["SECRET_KEY"] = 'secret'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
def index():
    #if there is no registered login session, redirect to login page
    if not session.get("name"):
        return redirect("/login")
    return render_template("index.html")

from auth import auth
app.register_blueprint(auth, url_prefix="/")

if __name__ == '__main__':
    #debug mode, turn off in deployment
    app.run(debug=True)