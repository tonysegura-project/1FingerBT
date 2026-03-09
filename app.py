from flask import Flask, render_template, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user

app = Flask(__name__)
app.secret_key = "supersecretkey123"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

data = {}
class Behavior(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    count = db.Column(db.Integer, default=0)
@app.route("/")
@login_required
def index():
    behaviors = Behavior.query.all()

    data = {b.name: b.count for b in behaviors}

    return render_template("index.html", data=data)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200))

@app.route("/add_behavior", methods=["POST"])
def add_behavior():
    behavior_name = request.json.get("behavior")

    if behavior_name:
        new_behavior = Behavior(name=behavior_name, count=0)
        db.session.add(new_behavior)
        db.session.commit()

    behaviors = Behavior.query.all()

    data = {b.name: b.count for b in behaviors}

    return jsonify(data)

@app.route("/update", methods=["POST"])
def update():
    behavior_name = request.json.get("behavior")

    behavior = Behavior.query.filter_by(name=behavior_name).first()

    if behavior:
        behavior.count += 1
        db.session.commit()

    behaviors = Behavior.query.all()

    data = {b.name: b.count for b in behaviors}

    return jsonify(data)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and user.password == password:
            login_user(user)
            return redirect("/")

    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run()

    #python app.py 

    
    