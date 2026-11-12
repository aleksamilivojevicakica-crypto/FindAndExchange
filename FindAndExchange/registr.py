import sqlite3
import hashlib
import secrets
from flask import request, render_template


def register():
    if request.method == "GET":
        return render_template("register.html")

    nickname = request.form.get("nickname", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    if not nickname or not email or len(password) < 8:
        return "Проверь введённые данные", 400

    salt = secrets.token_bytes(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        500000
    )

    password_hash = salt.hex() + ":" + password_hash.hex()

    connection = sqlite3.connect("findandexchange.db")

    try:
        connection.execute(
            "INSERT INTO users (nickname, email, password_h) VALUES (?, ?, ?)",
            (nickname, email, password_hash)
        )
        connection.commit()

    except sqlite3.IntegrityError:
        return "Такой email уже существует", 409

    finally:
        connection.close()

    return "Регистрация успешна!"