from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

data = {}

@app.route("/")
def index():
    return render_template("index.html", data=data)

@app.route("/add_behavior", methods=["POST"])
def add_behavior():
    behavior = request.json.get("behavior")
    if behavior and behavior not in data:
        data[behavior] = 0
    return jsonify(data)

@app.route("/update", methods=["POST"])
def update():
    behavior = request.json.get("behavior")
    if behavior in data:
        data[behavior] += 1
    return jsonify(data)

if __name__ == "__main__":
    app.run()
    #python app.py
    