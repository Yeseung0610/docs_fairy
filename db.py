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

    # folders 테이블
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS folders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        folder_name TEXT NOT NULL UNIQUE
    )
    ''')

    # pages 테이블: 기존 schema에 date 열 추가
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        page_name TEXT NOT NULL,
        folder_id INTEGER NOT NULL,
        content TEXT DEFAULT '',
        date TEXT DEFAULT '',
        FOREIGN KEY (folder_id) REFERENCES folders (id) ON DELETE CASCADE
    )
    ''')
    # 이미 생성된 테이블에 date 열이 없으면 추가
    cursor.execute("PRAGMA table_info(pages)")
    cols = [row[1] for row in cursor.fetchall()]
    if 'date' not in cols:
        cursor.execute("ALTER TABLE pages ADD COLUMN date TEXT DEFAULT ''")

    # chats, messages 테이블
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
        FOREIGN KEY (chat_name) REFERENCES chats (chat_name) ON DELETE CASCADE
    )
    ''')

    conn.commit()
    conn.close()

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
        FOREIGN KEY (chat_name) REFERENCES chats (chat_name) ON DELETE CASCADE
    )
    ''')
    conn.commit()
    conn.close()

# — 폴더·페이지 CRUD — #

def get_all_folders():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM folders ORDER BY id")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_folder(folder_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO folders (folder_name) VALUES (?)",
            (folder_name,)
        )
        conn.commit()
        result = True
    except sqlite3.IntegrityError:
        result = False
    conn.close()
    return result

def delete_folder(folder_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM folders WHERE id = ?", (folder_id,))
    conn.commit()
    conn.close()
    return True

def get_folder_pages(folder_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM pages WHERE folder_id = ? ORDER BY id",
        (folder_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_page(page_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pages WHERE id = ?", (page_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def add_page(page_name, folder_id, date_str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO pages (page_name, folder_id, date) VALUES (?, ?)",
        (page_name, folder_id, date_str)
    )
    conn.commit()
    conn.close()
    return True

def add_page_with_content(page_name, folder_id, content="", date_str=""):
    """내용과 날짜를 포함한 새 페이지를 생성합니다."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO pages (page_name, folder_id, content, date) VALUES (?, ?, ?, ?)",
        (page_name, folder_id, content, date_str)
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

def update_page_date(page_id, date):
    """페이지의 기록 날짜를 업데이트합니다."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE pages SET date = ? WHERE id = ?",
        (date, page_id)
    )
    conn.commit()
    conn.close()
    return True

# — 채팅 CRUD — #

def get_all_chats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT chat_name FROM chats ORDER BY id")
    rows = cursor.fetchall()
    conn.close()
    return [r['chat_name'] for r in rows]

def add_chat(chat_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chats (chat_name) VALUES (?)", (chat_name,))
    conn.commit()
    conn.close()
    return True

def delete_chat(chat_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE chat_name = ?", (chat_name,))
    cursor.execute("DELETE FROM chats WHERE chat_name = ?", (chat_name,))
    conn.commit()
    conn.close()
    return True

def get_chat_messages(chat_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, content FROM messages WHERE chat_name = ? ORDER BY id",
        (chat_name,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [{"role": r["role"], "content": r["content"]} for r in rows]

def add_message(chat_name, role, content):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (chat_name, role, content) VALUES (?, ?, ?)",
        (chat_name, role, content)
    )
    conn.commit()
    conn.close()
    return True
