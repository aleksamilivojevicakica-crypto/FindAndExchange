import sqlite3
import os
from flask import Flask, render_template

app = Flask(__name__)

database = "findandexchange.db"

if os.path.exists(database):
    print("База данных уже существует")
else:
    print("Базы данных нет. Создаём новую")
    connection = sqlite3.connect(database)
    connection.close()
    print("Новая база данных создана")


def get_db():
    connection = sqlite3.connect(database)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/categories")
def show_categories():
    conn = get_db()

    categories = conn.execute(
        "SELECT name FROM categories"
    ).fetchall()

    conn.close()

    result = []

    for category in categories:
        result.append(category[0])

    if len(result) > 0:
        return {"categories": result}
    else:
        return {"message": "Категорий пока нет"}


if __name__ == "__main__":
    app.run(debug=True)