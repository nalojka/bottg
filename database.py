import sqlite3
import logging

DB_FILE = "users.db"

# Настройка логирования
logging.basicConfig(filename="bot.log", level=logging.DEBUG, encoding="utf-8")

def create_db():
    """Создает таблицу пользователей, если её нет."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_user(user_id, username, first_name, last_name):
    """Добавляет пользователя в базу данных (если его ещё нет)."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO users (id, username, first_name, last_name) 
            VALUES (?, ?, ?, ?)
        """, (user_id, username, first_name, last_name))
        conn.commit()
        logging.info(f"Добавлен пользователь: {user_id}, {username}, {first_name} {last_name}")
    except Exception as e:
        logging.error(f"Ошибка при добавлении пользователя {user_id}: {e}")
    finally:
        conn.close()

def get_all_users():
    """Возвращает список ID всех пользователей."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users")
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    logging.info(f"Получены пользователи: {users}")
    return users

def get_user_list():
    """Возвращает форматированный список пользователей (ID + username + имя)."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, first_name, last_name FROM users")
    users = cursor.fetchall()
    conn.close()

    if not users:
        logging.warning("Список пользователей пуст!")
        return ["Список пользователей пуст!"]

    user_list = []
    for user in users:
        user_id, username, first_name, last_name = user
        username_text = f"(@{username})" if username else ""
        full_name = f"{first_name or ''} {last_name or ''}".strip()
        user_list.append(f"{user_id} {username_text} - {full_name}")

    logging.info(f"Список пользователей: {user_list}")
    return user_list
