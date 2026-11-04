import sqlite3

DATABASE = "findandexchange.db"


def create_database():
    conn = sqlite3.connect(DATABASE)
    conn.execute("PRAGMA foreign_keys = ON")

    cursor = conn.cursor()

    # 1. Пользователи
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. Категории
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)

    # 3. Вещи
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            category_id INTEGER,
            condition TEXT,
            desired_exchange TEXT,
            status TEXT NOT NULL DEFAULT 'available'
                CHECK(status IN (
                    'available', 'reserved', 'exchanged'
                )),
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (owner_id) REFERENCES users(id),
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    """)

    # 4. Фотографии вещей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS item_images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            image_path TEXT NOT NULL,
            sort_order INTEGER NOT NULL DEFAULT 0,

            FOREIGN KEY (item_id) REFERENCES items(id)
                ON DELETE CASCADE,
            UNIQUE(item_id, sort_order)
        )
    """)

    # 5. Анализ вещей искусственным интеллектом
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS item_ai_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            ai_description TEXT,
            ai_category_id INTEGER,
            estimated_value REAL,
            analyzed_at TEXT DEFAULT CURRENT_TIMESTAMP,
            model_name TEXT,

            FOREIGN KEY (item_id) REFERENCES items(id)
                ON DELETE CASCADE,
            FOREIGN KEY (ai_category_id) REFERENCES categories(id)
        )
    """)

    # 6. Заявки на обмен
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exchange_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending'
                CHECK(status IN (
                    'pending', 'accepted', 'rejected',
                    'cancelled', 'completed'
                )),
            source TEXT NOT NULL DEFAULT 'manual'
                CHECK(source IN ('manual', 'ai')),
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (sender_id) REFERENCES users(id),
            FOREIGN KEY (receiver_id) REFERENCES users(id),
            CHECK(sender_id != receiver_id)
        )
    """)

    # 7. Вещи в заявках
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exchange_request_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            role TEXT NOT NULL
                CHECK(role IN ('offered', 'requested')),

            FOREIGN KEY (request_id)
                REFERENCES exchange_requests(id)
                ON DELETE CASCADE,
            FOREIGN KEY (item_id) REFERENCES items(id),
            UNIQUE(request_id, item_id)
        )
    """)

    # 8. Автоматически найденные обмены
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exchange_matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_score REAL
                CHECK(match_score BETWEEN 0 AND 100),
            explanation TEXT,
            status TEXT NOT NULL DEFAULT 'suggested'
                CHECK(status IN (
                    'suggested', 'accepted',
                    'rejected', 'completed'
                )),
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 9. Вещи в найденных обменах
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS match_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER NOT NULL,
            item_id INTEGER NOT NULL,
            from_user_id INTEGER NOT NULL,
            to_user_id INTEGER NOT NULL,

            FOREIGN KEY (match_id)
                REFERENCES exchange_matches(id)
                ON DELETE CASCADE,
            FOREIGN KEY (item_id) REFERENCES items(id),
            FOREIGN KEY (from_user_id) REFERENCES users(id),
            FOREIGN KEY (to_user_id) REFERENCES users(id),

            UNIQUE(match_id, item_id),
            CHECK(from_user_id != to_user_id)
        )
    """)

    # Начальные категории
    categories = [
        "Electronics",
        "Clothing",
        "Books",
        "Sports",
        "Furniture",
        "Gaming",
        "Accessories",
        "Other"
    ]

    cursor.executemany("""
        INSERT OR IGNORE INTO categories (name)
        VALUES (?)
    """, [(category,) for category in categories])

    conn.commit()
    conn.close()

    print("FindAndExchange database created successfully!")


if __name__ == "__main__":
    create_database()
