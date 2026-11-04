from pathlib import Path
import sqlite3
from flask import Flask, render_template

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "findandexchange.db"

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)


# Подключение к базе данных
def get_db():
    if not DATABASE.is_file():
        raise FileNotFoundError(
            f"База данных не найдена: {DATABASE}"
        )

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# Главная страница
@app.route("/")
def index():
    return render_template("index.html")


# Проверка базы данных
@app.route("/test-db")
def test_db():
    conn = get_db()

    try:
        tables = conn.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' ORDER BY name"
        ).fetchall()

        return {
            "database": DATABASE.name,
            "tables": [row["name"] for row in tables]
        }
    finally:
        conn.close()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)

