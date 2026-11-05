import sqlite3

connect = sqlite3.connect("findandexchange.db")
connect.execute("PRAGMA foreign_keys = ON")

connect.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nickname TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_h TEXT NOT NULL,
    register_time TEXT DEFAULT CURRENT_TIMESTAMP
)
""")
connect.execute("""
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
)
""")
connect.execute("""
CREATE TABLE IF NOT EXISTS things(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    author_id INTEGER NOT NULL,
    receiver_id INTEGER,
    category_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    keywords TEXT NOT NULL,
    condition TEXT NOT NULL CHECK(condition IN ('awkward','bad', 'moderate', 'good', 'perfect')),
    FOREIGN KEY (author_id) REFERENCES users(id),
    FOREIGN KEY (receiver_id) REFERENCES users(id),
    FOREIGN KEY (category_id) REFERENCES categories(id))""")
connect.execute("""
CREATE TABLE IF NOT EXISTS images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thing_id INTEGER NOT NULL,
    image_path TEXT NOT NULL,
    FOREIGN KEY (thing_id) REFERENCES things(id)
)
""")
connect.execute("""
CREATE TABLE IF NOT EXISTS exchange_th (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    send_id INTEGER NOT NULL,
    get_id INTEGER NOT NULL,
    id_of_offered_thing INTEGER NOT NULL,
    id_of_wanted_thing INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'waited'
    CHECK(status IN ('waited', 'accepted', 'cancelled', 'denied')),
    FOREIGN KEY (send_id) REFERENCES users(id),
    FOREIGN KEY (get_id) REFERENCES users(id),
    FOREIGN KEY(id_of_offered_thing) REFERENCES things(id),
    FOREIGN KEY (id_of_wanted_thing) REFERENCES things(id)
)
""")
connect.execute("""
CREATE TABLE IF NOT EXISTS exchange_th_else_more (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    th_id INTEGER NOT NULL,
    thing_id INTEGER NOT NULL,
    type_of_thing TEXT NOT NULL CHECK(type_of_thing IN ('offered', 'wanted')),
    FOREIGN KEY (th_id) REFERENCES exchange_th(id),
    FOREIGN KEY (thing_id) REFERENCES things(id)
)
""")

connect.execute("""
CREATE TABLE IF NOT EXISTS exchange_ways (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL DEFAULT 'waited'
    CHECK(status IN ('waited', 'accepted', 'cancelled', 'completed'))
)
""")
connect.execute("""
CREATE TABLE IF NOT EXISTS ways_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    way_id INTEGER NOT NULL,
    from_id INTEGER NOT NULL,
    to_id INTEGER NOT NULL,
    thing_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'waited'
    CHECK(status IN ('waited', 'accepted', 'denied')),
    FOREIGN KEY (way_id) REFERENCES exchange_ways(id),
    FOREIGN KEY (from_id) REFERENCES users(id),
    FOREIGN KEY (to_id) REFERENCES users(id),
    FOREIGN KEY (thing_id) REFERENCES things(id)
)
""")

connect.execute("""
CREATE TABLE IF NOT EXISTS thing_ai_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thing_id INTEGER NOT NULL UNIQUE,
    ai_name TEXT,
    ai_description TEXT,
    ai_keywords TEXT,
    category_id INTEGER,
    analyzed_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (thing_id) REFERENCES things(id),
    FOREIGN KEY (category_id) REFERENCES categories(id)
)
""")
connect.execute("""
CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    way_id INTEGER NOT NULL UNIQUE,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (way_id) REFERENCES exchange_ways(id)
)
""")
connect.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
""")

categories = [
    "Electronics",
    "Clothes",
    "Sport",
    "Furniture",
    "Gaming",
    "Accessories",
    "Other"
]

for category in categories:
    connect.execute(
        "INSERT OR IGNORE INTO categories (name) VALUES (?)",
        (category,)
    )

connect.commit()
connect.close()

