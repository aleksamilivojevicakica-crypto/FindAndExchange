import os
import secrets
import sqlite3
from pathlib import Path
from flask import Flask, render_template, session, redirect, url_for, request

from registr import register
from login import login
from add import add_item

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

database = Path(__file__).resolve().parent / "findandexchange.db"


def get_db():
    if not database.exists():
        raise FileNotFoundError("Сначала запустить python data.py")
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@app.route("/")
def index():
    connection = get_db()
    try:
        rows = connection.execute("SELECT id, name FROM categories ORDER BY id").fetchall()
        names = {
            "Electronics": "Электроника", "Clothes": "Одежда",
            "Clothing": "Одежда", "Books": "Книги", "Sport": "Спорт",
            "Sports": "Спорт", "Furniture": "Мебель", "Gaming": "Игры",
            "Accessories": "Аксессуары", "Other": "Другое"
        }
        categories = [{"id": row["id"], "name": names.get(row["name"], row["name"])} for row in rows]

        search = request.args.get("search", "").strip()
        sql = """
            SELECT t.id, t.name AS title, t.description, t.condition,
                   (SELECT i.image_path FROM images i
                    WHERE i.thing_id = t.id ORDER BY i.id LIMIT 1) AS image_path
            FROM things t
        """
        selected_category = request.args.get("category", "")
        pattern = "%" + search + "%"

        if search and selected_category.isdigit():
            rows = connection.execute(
                sql + " WHERE (t.name LIKE ? OR t.description LIKE ?) AND t.category_id = ? ORDER BY t.id DESC",
                (pattern, pattern, int(selected_category))
            ).fetchall()
        elif search:
            rows = connection.execute(
                sql + " WHERE t.name LIKE ? OR t.description LIKE ? ORDER BY t.id DESC",
                (pattern, pattern)
            ).fetchall()
        elif selected_category.isdigit():
            rows = connection.execute(
                sql + " WHERE t.category_id = ? ORDER BY t.id DESC",
                (int(selected_category),)
            ).fetchall()
        else:
            rows = connection.execute(sql + " ORDER BY t.id DESC").fetchall()

        conditions = {
            "perfect": "Идеальное", "good": "Хорошее",
            "moderate": "Удовлетворительное", "bad": "Плохое",
            "awkward": "Очень плохое"
        }
        items = []
        for row in rows:
            item = dict(row)
            item["condition"] = conditions.get(item["condition"], item["condition"])
            marker = "\n\nЖелаемый обмен: "
            if marker in item["description"]:
                item["desired_exchange"] = "Хочу обменять на: " + item["description"].split(marker, 1)[1]
            else:
                item["desired_exchange"] = None
            items.append(item)
    finally:
        connection.close()

    return render_template("index.html", items=items, categories=categories, selected_category=selected_category)


@app.route("/categories")
def show_categories():
    connection = get_db()
    try:
        rows = connection.execute("SELECT name FROM categories ORDER BY id").fetchall()
        return {"categories": [row["name"] for row in rows]}
    finally:
        connection.close()


@app.route("/register", methods=["GET", "POST"])
def register_page():
    return register()


@app.route("/login", methods=["GET", "POST"])
def login_page():
    return login()


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/add", methods=["POST"])
def add_page():
    return add_item()


if __name__ == "__main__":
    app.run(debug=True)
