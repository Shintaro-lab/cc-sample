import sqlite3
import os
import streamlit as st
from pathlib import Path

# データベースファイルのパス
DB_PATH = Path("data/taskmanager.db")

# テストモード用のパス
TEST_DB_PATH = Path("app/data/test_taskmanager.db")

def get_connection():
    """データベース接続を取得"""
    # テストモードかどうかを確認
    if os.environ.get("TEST_MODE") == "1":
        db_path = TEST_DB_PATH
    else:
        db_path = DB_PATH
        
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """データベースとテーブルの初期化"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # ユーザーテーブルの作成
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # タスクテーブルの作成
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'not_started',
        priority TEXT DEFAULT 'medium',
        category TEXT,
        due_date TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    conn.commit()
    conn.close()

# Streamlitセッション状態の初期化
def init_session_state():
    """セッション状態の初期化"""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
