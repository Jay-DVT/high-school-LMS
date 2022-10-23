from flask import Flask, redirect, url_for, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from matplotlib.pyplot import get
from sqlalchemy.sql import func
# from os import path
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
# from flask_wtf import FlaskForm
# from wtforms import StringField, PasswordField, SubmitField
# from wtforms.validators import InputRequired, Length, ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
import random
import numpy

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

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(1000))
    answer = db.Column(db.String(1000))
    correct = db.Column(db.Boolean)
    topic = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    idValue = db.Column(db.String(150), unique=True)
    firstName = db.Column(db.String(150))
    lastName = db.Column(db.String(150))
    password = db.Column(db.String(150))
    notes = db.relationship('Note')
    questions = db.relationship('Question')


print('db init')
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

#*Routes
@app.route("/", methods=['GET', 'POST'])
@login_required
def index():
    return render_template("index.html", user=current_user)

#? ----------------- Authentication ----------------- 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        idValue = request.form.get('idValue')
        password = request.form.get('password')

        user = User.query.filter_by(idValue=idValue).first()
        if user:
            if check_password_hash(user.password, password):
                print('Logged in successfully!')
                login_user(user, remember=True)
                return redirect(url_for('index'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            print('idValue does not exist.')

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
        # elif len(password) < 7:
            # print('Password must be at least 7 characters.')
        else:
            new_user = User(idValue=idValue, firstName=firstName, lastName=lastName, password=generate_password_hash(password, method='sha256'))
            #generate_password_hash(password1, method='sha256')
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            print('Account created!')
            return redirect(url_for('index'))

    return render_template("signup.html", user=current_user)

#? ----------------------------------

#* ----------------- Subjects -----------------
@app.route('/math', methods=['GET', 'POST'])
@login_required
def math():
    return render_template("math.html", user=current_user)

@app.route('/physics', methods=['GET', 'POST'])
@login_required
def physics():
    return render_template("physics.html", user=current_user)

@app.route('/history', methods=['GET', 'POST'])
@login_required
def history():
    return render_template("history.html", user=current_user)
#* ----------------------------------

class Questions:
    def __init__(self, question, answer):
            self.question = question
            self.answer = answer

def validateAnswer(topic, result):
    questions = Question.query.filter_by(topic=topic, correct=False).all()
    for i in range(len(questions)):
        if result[i] == questions[i].answer:
            questions[i].correct = True
            print("True")
        else:
            questions[i].correct = False
            print("False")
    db.session.commit()
# ----------------- Math -----------------
# Algebra
@app.route('/math/scientific_notation/theory', methods=['GET'])
@login_required
def scientific_notation_theory():
    return render_template("scientific_notation.html", user=current_user, node="theory")
@app.route('/math/scientific_notation/practice', methods=['GET', 'POST'])
@login_required
def scientific_notation_practice():
    topic = "scientific_notation"
    if request.method == 'POST':
        result = list(request.form.values())
        validateAnswer(topic, result)
    finished = False
    corrects = 0
    questions = []
    ex = Question.query.filter_by(user_id=current_user.id, topic=topic).all()
    if ex:
        for i in range(len(ex)):
            if ex[i].correct == False:
                questions.append(Questions(ex[i].question, ex[i].answer))
            else:
                corrects += 1
        if corrects == len(ex):
            finished = True
    else:    
        for i in range(5):
            num = round(random.uniform(2, 10), 2)
            exp = random.randint(1, 12)
            question = str(num) + "\\times 10^{" + str(exp) + "}"
            answer = int(num * 10**exp)
            new_question = Question(question=question, answer=answer, correct=False, topic=topic, user_id=current_user.id)
            db.session.add(new_question)
            db.session.commit()
            questions.append(Questions(question, answer))
    return render_template("scientific_notation.html", user=current_user, node="practice", questions=questions, len=len(questions), finished=finished, score=corrects)

#lineal equations
@app.route('/math/lineal_equation/theory', methods=['GET'])
def lineal_equation_theory():
    return render_template("lineal_equation.html", user=current_user, node="theory")
@app.route('/math/lineal_equation/practice', methods=['GET', 'POST'])
def lineal_equation_practice():
    topic = "lineal_equation"
    if request.method == 'POST':
        result = list(request.form.values())
        validateAnswer(topic, result)
    finished = False
    corrects = 0
    questions = []
    ex = Question.query.filter_by(user_id=current_user.id, topic=topic).all()
    if ex:
        for i in range(len(ex)):
            if ex[i].correct == False:
                questions.append(Questions(ex[i].question, ex[i].answer))
            else:
                corrects += 1
        if corrects == len(ex):
            finished = True
    else:    
        for i in range(5):
            question = random.randint(1,3) + "
            answer =
            new_question = Question(question=question, answer=answer, correct=False, topic=topic, user_id=current_user.id)
            db.session.add(new_question)
            db.session.commit()
            questions.append(Questions(question, answer))
    return render_template("lineal_equation.html", user=current_user, node="practice", questions=questions, len=len(questions), finished=finished, score=corrects)
# ----------------------------------

# ----------------- Physics -----------------
# Metric systems
@app.route('/physics/metric_systems/theory', methods=['GET'])
def metric_systems_theory():
    return render_template("metric_systems.html", user=current_user, node="theory")
@app.route('/physics/metric_systems/practice', methods=['GET', 'POST'])
def metric_systems_practice():
    return render_template("metric_systems.html", user=current_user, node="practice")

# line movement
@app.route('/physics/line_movement/theory', methods=['GET'])
def line_movement_theory():
    return render_template("line_movement.html", user=current_user, node="theory")
@app.route('/physics/line_movement/practice', methods=['GET', 'POST'])
def line_movement_practice():
    return render_template("line_movement.html", user=current_user, node="practice")

# Force
@app.route('/physics/force/theory', methods=['GET'])
def force_theory():
    return render_template("force.html", user=current_user, node="theory")
@app.route('/physics/force/practice', methods=['GET', 'POST'])
def force_practice():
    return render_template("force.html", user=current_user, node="practice")
# ----------------------------------

# ----------------- History -----------------
# Nation state
@app.route('/history/nation_state/theory', methods=['GET'])
def nation_state_theory():
    return render_template("nation_state.html", user=current_user, node="theory")
@app.route('/history/nation_state/practice', methods=['GET', 'POST'])
def nation_state_practice():
    return render_template("nation_state.html", user=current_user, node="practice")
# ----------------------------------

if __name__ == '__main__':
    #debug mode, turn off in deployment
    app.run(debug=True)