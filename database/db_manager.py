import sqlite3
import os

# Ensure the database file is created inside your 'database' folder
DB_PATH = os.path.join(os.path.dirname(__file__), "avianquest.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    """Creates the necessary tables if they don't exist yet."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Table for Chat Sessions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id TEXT PRIMARY KEY,
            title TEXT
        )
    """)
    
    # Table for Individual Messages
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT,
            role TEXT,
            text_content TEXT,
            FOREIGN KEY(chat_id) REFERENCES chats(id)
        )
    """)
    conn.commit()
    conn.close()

def create_chat(chat_id, title):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chats (id, title) VALUES (?, ?)", (chat_id, title))
    conn.commit()
    conn.close()

def update_chat_title(chat_id, new_title):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE chats SET title = ? WHERE id = ?", (new_title, chat_id))
    conn.commit()
    conn.close()

def save_message(chat_id, role, text_content):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (chat_id, role, text_content) VALUES (?, ?, ?)", 
                   (chat_id, role, text_content))
    conn.commit()
    conn.close()

def get_all_chats():
    """Returns a list of dictionaries containing chat IDs and titles."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title FROM chats")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": row[0], "title": row[1]} for row in rows]

def get_chat_messages(chat_id):
    """Returns all messages for a specific chat ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role, text_content FROM messages WHERE chat_id = ? ORDER BY id ASC", (chat_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"role": row[0], "text": row[1]} for row in rows]