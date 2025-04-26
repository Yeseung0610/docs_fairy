import sqlite3
import os

def get_db_connection():
    """데이터베이스 연결을 생성하여 반환합니다."""
    if not os.path.exists('data'):
        os.makedirs('data')
    conn = sqlite3.connect('data/task_assistant.db')
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db():
    """테이블이 없으면 폴더·페이지 테이블을 생성합니다."""
    conn = get_db_connection()
    cursor = conn.cursor()

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

def get_all_folders():
    """모든 폴더를 이름순으로 반환합니다."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM folders ORDER BY folder_name")
    folders = cursor.fetchall()
    conn.close()
    return folders

def get_folder_pages(folder_id):
    """특정 폴더의 페이지 목록을 이름순으로 반환합니다."""
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
    """단일 페이지 정보를 반환합니다."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pages WHERE id = ?", (page_id,))
    page = cursor.fetchone()
    conn.close()
    return page

def add_folder(folder_name):
    """새 폴더를 추가합니다. (이름 중복 시 False 반환)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO folders (folder_name) VALUES (?)", (folder_name,))
        conn.commit()
        result = True
    except sqlite3.IntegrityError:
        result = False
    finally:
        conn.close()
    return result

# def add_page(page_name, folder_id):
#     """새 페이지를 폴더에 추가합니다."""
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute(
#         "INSERT INTO pages (page_name, folder_id) VALUES (?, ?)",
#         (page_name, folder_id)
#     )
#     conn.commit()
#     conn.close()
#     return True

def add_page_with_content(page_name, folder_id, content=""):
    """내용을 포함한 새 페이지를 폴더에 추가합니다."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO pages (page_name, folder_id, content) VALUES (?, ?, ?)",
            (page_name, folder_id, content)
        )
        conn.commit()
        # 방금 삽입한 페이지의 ID 반환
        page_id = cursor.lastrowid
        conn.close()
        return page_id
    except Exception as e:
        print(f"페이지 추가 오류: {e}")
        conn.close()
        return None

def update_page_content(page_id, content):
    """페이지의 내용을 갱신하여 저장합니다."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE pages SET content = ? WHERE id = ?",
        (content, page_id)
    )
    conn.commit()
    conn.close()
    return True

def delete_page(page_id):
    """페이지를 삭제합니다."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pages WHERE id = ?", (page_id,))
    conn.commit()
    conn.close()
    return True

def delete_folder(folder_id):
    """폴더 및 그 하위 페이지를 모두 삭제합니다."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM pages WHERE folder_id = ?", (folder_id,))
    cursor.execute("DELETE FROM folders WHERE id = ?", (folder_id,))
    conn.commit()
    conn.close()
    return True
