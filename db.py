import sqlite3
import os

def get_db_connection():
    """데이터베이스 연결을 생성하여 반환합니다."""
    if not os.path.exists('data'):
        os.makedirs('data')
    conn = sqlite3.connect('data/task_assistant.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db():
    """메인 테이블이 없으면 생성하고, 채팅용 테이블도 초기화합니다."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # 폴더·페이지 테이블 생성
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS folders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        folder_name TEXT NOT NULL UNIQUE
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        page_name TEXT NOT NULL,
        folder_id INTEGER NOT NULL,
        content TEXT DEFAULT '',
        FOREIGN KEY (folder_id) REFERENCES folders (id) ON DELETE CASCADE
    )
    ''')
    conn.commit()
    conn.close()

    # 채팅용 테이블 생성
    initialize_chat_db()

def initialize_chat_db():
    """채팅 목록과 메시지 테이블을 생성합니다."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_name TEXT NOT NULL UNIQUE
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_name TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (chat_name) REFERENCES chats (chat_name) ON DELETE CASCADE
    )
    ''')
    conn.commit()
    conn.close()

# -------------- 폴더·페이지 CRUD --------------

def get_all_folders():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM folders ORDER BY folder_name")
    folders = cursor.fetchall()
    conn.close()
    return folders

def add_folder(folder_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO folders (folder_name) VALUES (?)", (folder_name,))
        conn.commit()
        result = True
    except sqlite3.IntegrityError:
        result = False
    conn.close()
    return result

def delete_folder(folder_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pages WHERE folder_id = ?", (folder_id,))
    cursor.execute("DELETE FROM folders WHERE id = ?", (folder_id,))
    conn.commit()
    conn.close()
    return True

def get_pages_in_folder(folder_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM pages WHERE folder_id = ? ORDER BY page_name",
        (folder_id,)
    )
    pages = cursor.fetchall()
    conn.close()
    return pages

def get_page(page_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pages WHERE id = ?", (page_id,))
    page = cursor.fetchone()
    conn.close()
    return page

def add_page(page_name, folder_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO pages (page_name, folder_id) VALUES (?, ?)",
        (page_name, folder_id)
    )
    conn.commit()
    conn.close()
    return True

def delete_page(page_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pages WHERE id = ?", (page_id,))
    conn.commit()
    conn.close()
    return True

def update_page_content(page_id, content):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE pages SET content = ? WHERE id = ?",
        (content, page_id)
    )
    conn.commit()
    conn.close()
    return True

# -------------- 채팅용 CRUD --------------

def get_all_chats():
    """모든 채팅 탭 이름을 생성 순서대로 반환합니다."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT chat_name FROM chats ORDER BY id")
    rows = cursor.fetchall()
    conn.close()
    return [row['chat_name'] for row in rows]

def add_chat(chat_name):
    """새 채팅 탭을 추가합니다. (이름 중복 시 False 반환)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO chats (chat_name) VALUES (?)", (chat_name,))
        conn.commit()
        result = True
    except sqlite3.IntegrityError:
        result = False
    conn.close()
    return result

def delete_chat(chat_name):
    """채팅 탭과 해당 메시지를 모두 삭제합니다."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE chat_name = ?", (chat_name,))
    cursor.execute("DELETE FROM chats WHERE chat_name = ?", (chat_name,))
    conn.commit()
    conn.close()
    return True

def get_chat_messages(chat_name):
    """특정 채팅 탭에 속한 메시지를 순서대로 반환합니다."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, content FROM messages WHERE chat_name = ? ORDER BY id",
        (chat_name,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [{"role": row['role'], "content": row['content']} for row in rows]

def add_message(chat_name, role, content):
    """채팅 메시지를 기록합니다."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (chat_name, role, content) VALUES (?, ?, ?)",
        (chat_name, role, content)
    )
    conn.commit()
    conn.close()
    return True
