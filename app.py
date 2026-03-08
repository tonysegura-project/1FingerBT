from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

data = {}
class Behavior(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    count = db.Column(db.Integer, default=0)
@app.route("/")
def index():
    return render_template("index.html", data=data)

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

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run()

    #python app.py
    