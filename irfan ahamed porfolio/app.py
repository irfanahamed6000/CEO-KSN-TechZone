import os
import threading
from datetime import datetime

from flask import Flask, request, jsonify, send_from_directory, abort

BASE = os.path.dirname(os.path.abspath(__file__))
MESSAGES_FILE = os.path.join(BASE, "messages.txt")

app = Flask(__name__, static_folder=None)
lock = threading.Lock()


def one_line(value, limit):
    """Trim, cap the length and remove line breaks."""
    return " ".join(str(value or "").split())[:limit]


@app.get("/")
def home():
    return send_from_directory(BASE, "index.html")


def norm(text):
    """Lowercase and keep only letters and digits, so 'MJ Traders' matches 'mj-traders'."""
    return "".join(ch for ch in text.lower() if ch.isalnum())


@app.get("/images/<path:name>")
def images(name):
    folder = os.path.join(BASE, "images")
    stem, ext = os.path.splitext(name)
    if os.path.isdir(folder):
        for f in os.listdir(folder):
            fstem, fext = os.path.splitext(f)
            if fext.lower() == ext.lower() and norm(fstem) == norm(stem):
                return send_from_directory(folder, f)
    abort(404)


@app.post("/contact")
def contact():
    data = request.get_json(silent=True) or {}
    name = one_line(data.get("name"), 100)
    email = one_line(data.get("email"), 150)
    message = str(data.get("message") or "").strip()[:3000]

    if not name or "@" not in email or not message:
        return jsonify(ok=False, error="Please fill in all fields."), 400

    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = (
        "=" * 50 + "\n"
        f"Date   : {stamp}\n"
        f"Name   : {name}\n"
        f"Email  : {email}\n"
        f"Message: {message}\n\n"
    )
    with lock, open(MESSAGES_FILE, "a", encoding="utf-8") as f:
        f.write(entry)
    return jsonify(ok=True)


if __name__ == "__main__":
    print("Open http://127.0.0.1:5000 in your browser")
    app.run(host="127.0.0.1", port=5000)
