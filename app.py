from flask import Flask, redirect, url_for, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
# from os import path
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
# from flask_wtf import FlaskForm
# from wtforms import StringField, PasswordField, SubmitField
# from wtforms.validators import InputRequired, Length, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()
DB_NAME = "students.db"

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#* login start
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'



db.init_app(app)
#* Database Models

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    idValue = db.Column(db.String(150), unique=True)
    firstName = db.Column(db.String(150))
    lastName = db.Column(db.String(150))
    password = db.Column(db.String(150))
    notes = db.relationship('Note')


print('db init')
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

#*Routes
@app.route("/")
def index():
    #if there is no registered login session, redirect to login page
    return redirect("/login")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        idValue = request.form.get('idValue')
        password = request.form.get('password')

        user = User.query.filter_by(idValue=idValue).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('idValue does not exist.', category='error')

    return render_template("login.html", user=current_user)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        idValue = request.form.get('idValue')
        firstName = request.form.get('firstName')
        lastName = request.form.get('lastName')
        password = request.form.get('password')
        passwordConfirm = request.form.get('passwordConfirm')
        print(request.form)

        user = User.query.filter_by(idValue=idValue).first()
        print("1")
        if user:
            print('idValue already exists.')
        elif password != passwordConfirm:
            print('Passwords don\'t match.')
        elif len(password) < 7:
            print('Password must be at least 7 characters.')
        else:
            new_user = User(idValue=idValue, firstName=firstName, lastName=lastName, password=generate_password_hash(password, method='sha256'))
            #generate_password_hash(password1, method='sha256')
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            print('Account created!')
            return redirect(url_for('index'))

    return render_template("signup.html", user=current_user)

if __name__ == '__main__':
    #debug mode, turn off in deployment
    app.run(debug=True)