import sqlite3
import hashlib
import hmac
from pathlib import Path
from flask import request, render_template, redirect, session


def check_password(password, saved):
    try:
        salt, password_hash = saved.split(":")

        result = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            bytes.fromhex(salt),
            500000
        )

        return hmac.compare_digest(result, bytes.fromhex(password_hash))
    except (ValueError, TypeError, AttributeError):
        return False


def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not email or not password:
        return render_template("login.html", error="Введите email и пароль"), 400

    db = sqlite3.connect(Path(__file__).with_name("findandexchange.db"))

    user = db.execute(
        "SELECT id, nickname, password_h FROM users WHERE email = ?",
        (email,)
    ).fetchone()

    db.close()

    if user is None or not check_password(password, user[2]):
        return render_template("login.html", error="Неверный email или пароль")

    session.clear()
    session["user_id"] = user[0]
    session["nickname"] = user[1]

    return redirect("/")
