from operator import le
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
    value = db.Column(db.String(100))
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
    def __init__(self, question, answer, value):
            self.question = question
            self.answer = answer
            self.value = value

def validateAnswerfloat(topic, result, roundness):
    questions = Question.query.filter_by(topic=topic, correct=False).all()
    for i in range(len(questions)):
        print(result[i], questions[i].answer)
        if result[i] == "":
            print("False")
            questions[i].correct = False
        elif float(result[i]) <= float(questions[i].answer) + roundness or float(result[i]) >= float(questions[i].answer) - roundness:
            questions[i].correct = True
            print("True")
        else:
            questions[i].correct = False
            print("False")
        db.session.commit()

def validateAnswerRadio(topic, result):
    questions = Question.query.filter_by(topic=topic, correct=False).all()
    for i in range(len(questions)):
        value = questions[i].value.split(",")
        print(value[int(result[i])], questions[i].answer)
        if value[int(result[i])] == questions[i].answer:
            print("True")
            questions[i].correct = True
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
        validateAnswerfloat(topic, result, 0)
    finished = False
    corrects = 0
    questions = []
    ex = Question.query.filter_by(user_id=current_user.id, topic=topic).all()
    if ex:
        for i in range(len(ex)):
            if ex[i].correct == False:
                questions.append(Questions(ex[i].question, ex[i].answer, None))
            else:
                corrects += 1
        if corrects == len(ex):
            finished = True
    else:    
        for i in range(5):
            num = round(random.uniform(2, 10), 2)
            exp = random.randint(3, 12)
            question = str(num) + "\\times 10^{" + str(exp) + "}"
            answer = int(num * 10**exp)
            new_question = Question(question=question, answer=answer, correct=False, topic=topic, user_id=current_user.id)
            db.session.add(new_question)
            db.session.commit()
            questions.append(Questions(question, answer, None))
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
        roundness = 0.1
        validateAnswerfloat(topic, result, roundness)
    finished = False
    corrects = 0
    questions = []
    ex = Question.query.filter_by(user_id=current_user.id, topic=topic).all()
    if ex:
        for i in range(len(ex)):
            if ex[i].correct == False:
                questions.append(Questions(ex[i].question, ex[i].answer, None))
            else:
                corrects += 1
        if corrects == len(ex):
            finished = True
    else:    
        for i in range(5):
            x_1 = int()
            x_2 = int()
            const_1 = int()
            const_2 = int()
            while x_1 == 0 or x_1 == 1:
                x_1 = random.randint(-10, 10)
            while x_2 == 0 or x_2 == 1:
                x_2 = random.randint(-10, 10)
            while const_1 == 0:
                const_1 = random.randint(-10, 30)
            while const_2 == 0:
                const_2 = random.randint(-10, 30)
            case = random.randint(1, 2)
            if case == 1:
                question =  str(x_1) + "x + (" + str(const_1) + ") = " + str(x_2) + "x + (" + str(const_2) + ")"
                answer = round((const_2 - const_1)/(x_1 - x_2), 2)
            elif case == 2:
                mult_1 = random.randint(2, 5)
                mult_2 = random.randint(2, 5)
                print(mult_1, mult_2)
                question = str(mult_1) + "(" + str(x_1) + "x) + (" + str(const_1) + ") = " + str(mult_2) + "(" + str(x_2) + "x) + (" + str(const_2) + ")"
                answer = round((const_2 - const_1)/(x_1*mult_1 - x_2*mult_2), 2)
            new_question = Question(question=question, answer=answer, correct=False, topic=topic, user_id=current_user.id)
            db.session.add(new_question)
            db.session.commit()
            questions.append(Questions(question, answer, None))
    return render_template("lineal_equation.html", user=current_user, node="practice", questions=questions, len=len(questions), finished=finished, score=corrects)
# ----------------------------------

# ----------------- Physics -----------------
# Metric systems
@app.route('/physics/metric_systems/theory', methods=['GET'])
def metric_systems_theory():
    return render_template("metric_systems.html", user=current_user, node="theory")
@app.route('/physics/metric_systems/practice', methods=['GET', 'POST'])
def metric_systems_practice():
    topic = "metric_systems"
    if request.method == 'POST':
        result = list(request.form.values())
        roundness = 0.1
        validateAnswerfloat(topic, result, roundness)
    finished = False
    corrects = 0
    questions = []
    ex = Question.query.filter_by(user_id=current_user.id, topic=topic).all()
    if ex:
        for i in range(len(ex)):
            if ex[i].correct == False:
                questions.append(Questions(ex[i].question, ex[i].answer, ex[i].value)) #ex[i].value
            else:
                corrects += 1
        if corrects == len(ex):
            finished = True
    else:
        for i in range(20):
            if i < 5: #Length
                case = random.randint(1, 10)
                num = random.randint(1, 100)
                if case == 1: #km to m
                    question = str(num) + " km"
                    answer = str(num * 1000)
                    value = "m"
                elif case == 2: #m to km
                    question = str(num) + " m"
                    answer = str(num * 0.001)
                    value = "km"
                elif case == 3: #m to cm
                    question = str(num) + " m"
                    answer = str(num * 100)
                    value = "cm"
                elif case == 4: #cm to m
                    question = str(num) + " cm"
                    answer = str(num * 0.01)
                    value = "m"
                elif case == 5: #feet to m
                    question = str(num) + " ft"
                    answer = str(num / 3.281)
                    value = "m"
                elif case == 6: #m to feet
                    question = str(num) + " m"
                    answer = str(num * 3.281)
                    value = "ft"
                elif case == 7: #inches to cm
                    question = str(num) + " in"
                    answer = str(num * 2.54)
                    value = "cm"
                elif case == 8: #cm to inches
                    question = str(num) + " cm"
                    answer = str(num / 2.54)
                    value = "in"
                elif case == 9: #miles to km
                    question = str(num) + " mi"
                    answer = str(num * 1.609)
                    value = "km"
                else: #km to miles
                    question = str(num) + " km"
                    answer = str(num / 1.609)
                    value = "mi"
            elif i < 10: #Mass
                case = random.randint(1, 4)
                num = random.randint(1, 100)
                if case == 1: #kg to g
                    question = str(num) + " kg"
                    answer = str(num * 1000)
                    value = "g"
                elif case == 2: #g to kg
                    question = str(num) + " g"
                    answer = str(num * 0.001)
                    value = "kg"
                elif case == 3: #lb to kg
                    question = str(num) + " lb"
                    answer = str(num / 2.205)
                    value = "kg"
                else: #kg to lb
                    question = str(num) + " kg"
                    answer = str(num * 2.205)
                    value = "lb"
            elif i < 15: #Volume
                case = random.randint(1, 4)
                num = random.randint(1, 100)
                if case == 1: #L to ml
                    question = str(num) + " L"
                    answer = str(num * 1000)
                    value = "mL"
                elif case == 2: #ml to L
                    question = str(num) + " ml"
                    answer = str(num * 0.001)
                    value = "L"
                elif case == 3: #gal to L
                    question = str(num) + " gal"
                    answer = str(num * 3.785)
                    value = "L"
                else: #L to gal
                    question = str(num) + " L"
                    answer = str(num / 3.785)
                    value = "gal"
            else: #Time
                case = random.randint(1, 4)
                num = random.randint(1, 100)
                if case == 1: #s to ms
                    question = str(num) + " s"
                    answer = str(num * 1000)
                    value = "ms"
                elif case == 2: #ms to s
                    question = str(num) + " ms"
                    answer = str(num * 0.001)
                    value = "s"
                elif case == 3: #min to s
                    question = str(num) + " min"
                    answer = str(num * 60)
                    value = "s"
                else: #s to min
                    question = str(num) + " s"
                    answer = str(num / 60)
                    value = "min"
            new_question = Question(question=question, answer=answer, correct=False, topic=topic, value=value, user_id=current_user.id)
            db.session.add(new_question)
            db.session.commit()
            questions.append(Questions(question, answer, value))
    return render_template("metric_systems.html", user=current_user, node="practice", questions=questions, len=len(questions), finished=finished, score=corrects)
# ----------------------------------

# ----------------- History -----------------
# Nation state
@app.route('/history/conquista/theory', methods=['GET'])
def conquista_theory():
    return render_template("conquista.html", user=current_user, node="theory")
@app.route('/history/conquista/practice', methods=['GET', 'POST'])
def conquista_practice():
    topic = "conquista"
    if request.method == 'POST':
        result = list(request.form.values())
        print(result)
        validateAnswerRadio(topic, result)
    finished = False
    corrects = 0
    questions = []
    ex = Question.query.filter_by(user_id=current_user.id, topic=topic).all()
    if ex:
        length = 0
        for i in range(len(ex)):
            if ex[i].correct == False:
                print(ex[i].question)
                value = ex[i].value.split(",")
                questions.append(Questions(ex[i].question, ex[i].answer, value)) #ex[i].value
                length += 1
            else:
                corrects += 1
        if corrects == len(ex):
            finished = True
    else:
        questionls = [
            {"question": "¿Cuántas órdenes de frailes llegaron a la Nueva España a evangelizar?", "answer": "3", "value": ["3", "7", "5", "2"]},
            {"question": "¿Cuál fue la primera orden de frailes que llegó a la Nueva España?", "answer": "Franciscanos", "value": ["Franciscanos", "Dominicos", "Agustinos", "Mercedarios"]},
            {"question": "¿Cuál fue la tercera orden de frailes que llegó a la Nueva España?", "answer": "Agustinos", "value": ["Franciscanos", "Dominicos", "Agustinos", "Mercedarios"]},
            {"question": "¿Quién fue el primer virrey de la Nueva España?", "answer": "Antonio de Mendoza", "value": ["Leopoldo I", "Maximiliano II", "Antonio de Mendoza", "Josefa I"]},
            {"question": "¿Cuándo llegó?", "answer": "1535", "value": ["1535", "1577", "1525", "1582"]},
            {"question": "¿Quién nombraba al Virrey?", "answer": "El monarca español", "value": ["El monarca español", "Consejo local", "El vato ese", "El mismo virrey"]},
            {"question": "¿Quién o quiénes eran la máxima autoridad en la Nueva España?", "answer": "El consejo de indias", "value": ["El consejo de espana", "El virrey", "El pueblo", "El consejo de indias"]},
            {"question": "¿Qué hacían los encomenderos?", "answer": "Controlar a los pueblos indígenas", "value": ["Controlar a los pueblos indígenas", "Apoya a los pueblos indígenas", "sepa", "llamrle al virrey"]},
            {"question": "¿Cuántos virreyes hubieron durante el virreinato?", "answer": "63", "value": ["63", "7", "13", "3"]},
            {"question": "¿En qué se basaba la organización social de la Nueva España?", "answer": "origen de los individuos", "value": ["religion", "procedencia de la casa", "origen de los individuos", "origen del ganado"]},]
        length = len(questionls)
        print(length)  
        for i in range(length):
            question = questionls[i]["question"]
            answer = questionls[i]["answer"]
            value = questionls[i]["value"]
            saveValue = ",".join(value)
            new_question = Question(question=question, answer=answer, correct=False, topic=topic, value=saveValue, user_id=current_user.id)
            db.session.add(new_question)
            db.session.commit()
            questions.append(Questions(question, answer, value))
    return render_template("conquista.html", user=current_user, node="practice", questions=questions, len=length, finished=finished, score=corrects)
# ----------------------------------

if __name__ == '__main__':
    #debug mode, turn off in deployment
    app.run(debug=True)