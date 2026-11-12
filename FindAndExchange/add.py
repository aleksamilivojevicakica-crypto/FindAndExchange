import sqlite3
import secrets
from pathlib import Path
from flask import request, redirect, session


def add_item():
    if "user_id" not in session:
        return redirect("/login")

    name = request.form.get("title", "").strip()
    description = request.form.get("description", "").strip()
    desired = request.form.get("desired_exchange", "").strip()
    category = request.form.get("category_id", "")
    condition = request.form.get("condition", "")

    photos = []
    for photo in request.files.getlist("photos"):
        if photo.filename:
            photos.append(photo)

    if not name or len(name) > 120:
        return "Название должно содержать от 1 до 120 символов", 400
    if not description or len(description) > 2000:
        return "Описание должно содержать от 1 до 2000 символов", 400
    if len(desired) > 500:
        return "Слишком длинное пожелание обмена", 400
    if not category.isdigit():
        return "Выберите категорию", 400
    if condition not in ["perfect", "good", "moderate", "bad", "awkward"]:
        return "Неверное состояние вещи", 400
    if len(photos) > 5:
        return "Можно загрузить максимум 5 фотографий", 400

    for photo in photos:
        if "." not in photo.filename:
            return "Неправильное название фотографии", 400

        extension = photo.filename.rsplit(".", 1)[1].lower()
        header = photo.stream.read(16)
        photo.stream.seek(0)

        if extension in ["jpg", "jpeg"]:
            if not header.startswith(b"\xff\xd8\xff"):
                return "Файл JPG повреждён или не является фотографией", 400
        elif extension == "png":
            if not header.startswith(b"\x89PNG\r\n\x1a\n"):
                return "Файл PNG повреждён или не является фотографией", 400
        elif extension == "webp":
            if header[:4] != b"RIFF" or header[8:12] != b"WEBP":
                return "Файл WebP повреждён или не является фотографией", 400
        else:
            return "Звмените на JPG, PNG или WebP", 400

    if desired:
        description += "\n\nЖелаемый обмен: " + desired

    database = Path(__file__).with_name("findandexchange.db")
    folder = Path(__file__).resolve().parent / "static" / "uploads"
    saved_files = []

    db = sqlite3.connect(database)
    db.execute("PRAGMA foreign_keys = ON")

    try:
        found = db.execute(
            "SELECT id FROM categories WHERE id = ?", (int(category),)
        ).fetchone()
        if found is None:
            return "Такой категории нет", 400

        cursor = db.execute("""
            INSERT INTO things
            (name, author_id, category_id, description, keywords, condition)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, session["user_id"], int(category), description,
              name.lower(), condition))

        thing_id = cursor.lastrowid
        folder.mkdir(parents=True, exist_ok=True)

        for photo in photos:
            extension = photo.filename.rsplit(".", 1)[1].lower()
            filename = secrets.token_hex(16) + "." + extension
            path = folder / filename
            saved_files.append(path)
            photo.save(str(path))
            db.execute(
                "INSERT INTO images (thing_id, image_path) VALUES (?, ?)",
                (thing_id, "uploads/" + filename)
            )

        db.commit()
    except (sqlite3.Error, OSError):
        db.rollback()
        for path in saved_files:
            if path.exists():
                path.unlink()
        return "Ошибка при сохранении объявления", 500
    finally:
        db.close()

    return redirect("/#catalog")
