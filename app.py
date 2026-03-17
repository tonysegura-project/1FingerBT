import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, send_file, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# --- Updated Configuration Section ---
app.config['SECRET_KEY'] = "aba_tracker_secret_key"
app.config['SESSION_PERMANENT'] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///behavior_tracker.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# ---------------- MODELS ----------------

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    sessions = db.relationship('Session', backref='user', lazy=True)

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False) # Client Name
    date = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    behaviors = db.relationship('Behavior', backref='session', cascade="all, delete-orphan", lazy=True)

class Behavior(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    count = db.Column(db.Integer, default=0)
    session_id = db.Column(db.Integer, db.ForeignKey("session.id"), nullable=False)

# ---------------- ROUTES ----------------

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if User.query.filter_by(email=email).first():
            flash("Email already exists.")
            return redirect(url_for("signup"))
        new_user = User(email=email, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=False)
            return redirect(url_for("index"))
        flash("Invalid credentials.")
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# ---------------- API DATA ROUTES ----------------

@app.route("/create_session", methods=["POST"])
@login_required
def create_session():
    data = request.json
    new_session = Session(name=data['name'], date=data['date'], user_id=current_user.id)
    db.session.add(new_session)
    db.session.commit()
    return get_sessions()

@app.route("/get_sessions")
@login_required
def get_sessions():
    sessions = Session.query.filter_by(user_id=current_user.id).all()
    return jsonify([{"id": s.id, "name": s.name, "date": s.date} for s in sessions])

@app.route("/get_behaviors/<int:session_id>")
@login_required
def get_behaviors(session_id):
    behaviors = Behavior.query.filter_by(session_id=session_id).all()
    return jsonify({b.name: b.count for b in behaviors})

@app.route("/add_behavior", methods=["POST"])
@login_required
def add_behavior():
    data = request.json
    session_id = data.get("session_id")
    name = data.get("behavior")
    
    existing = Behavior.query.filter_by(name=name, session_id=session_id).first()
    if not existing:
        new_b = Behavior(name=name, count=0, session_id=session_id)
        db.session.add(new_b)
        db.session.commit()
    return get_behaviors(session_id)

@app.route("/update_count", methods=["POST"])
@login_required
def update_count():
    data = request.json
    behavior = Behavior.query.filter_by(name=data['behavior'], session_id=data['session_id']).first()
    if behavior:
        behavior.count += 1
        db.session.commit()
    return get_behaviors(data['session_id'])

@app.route("/delete_session/<int:session_id>", methods=["POST"])
@login_required
def delete_session(session_id):
    session = Session.query.get(session_id)
    if session and session.user_id == current_user.id:
        db.session.delete(session)
        db.session.commit()
    return get_sessions()

# ---------------- PWA ROUTES ----------------

@app.route('/manifest.json')
def serve_manifest():
    try:
        base_dir = os.path.abspath(os.path.dirname(__file__))
        return send_file(os.path.join(base_dir, 'manifest.json'), mimetype='application/json')
    except Exception as e:
        return str(e), 404

@app.route('/sw.js')
def serve_sw():
    try:
        base_dir = os.path.abspath(os.path.dirname(__file__))
        return send_file(os.path.join(base_dir, 'sw.js'), mimetype='application/javascript')
    except Exception as e:
        return str(e), 404

#------------------LOGO PNG------------------   

@app.route('/logo.png')
def serve_logo():
    try:
        # This looks inside your new 'static' folder
        return send_from_directory('static', 'logo.png')
    except Exception as e:
        return str(e), 404

# ---------------- STARTUP ----------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    
    # Corrected Render Port Logic
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)