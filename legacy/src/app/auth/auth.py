from passlib.hash import pbkdf2_sha256
import streamlit as st
from utils.db import get_connection

def hash_password(password):
    """パスワードをハッシュ化"""
    return pbkdf2_sha256.hash(password)

def verify_password(password, hash):
    """パスワードの検証"""
    return pbkdf2_sha256.verify(password, hash)

def register_user(username, password, test_mode=False):
    """新規ユーザー登録
    
    Args:
        username: ユーザー名
        password: パスワード
        test_mode: テストモード（Trueの場合、DB接続を閉じない）
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # ユーザー名の重複チェック
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            if not test_mode:
                conn.close()
            return False, "このユーザー名は既に使用されています"
        
        # パスワードのハッシュ化と登録
        hashed_password = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_password)
        )
        conn.commit()
        if not test_mode:
            conn.close()
        return True, "ユーザー登録が完了しました"
    except Exception as e:
        if not test_mode:
            conn.close()
        return False, f"登録エラー: {str(e)}"

def login_user(username, password):
    """ユーザーログイン"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # ユーザー名の確認
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return False, "ユーザー名が見つかりません"
    
    # パスワードの検証
    if verify_password(password, user['password']):
        # セッション状態を更新
        st.session_state.user_id = user['id']
        st.session_state.username = user['username']
        st.session_state.authenticated = True
        conn.close()
        return True, "ログインに成功しました"
    else:
        conn.close()
        return False, "パスワードが正しくありません"

def logout_user():
    """ユーザーログアウト"""
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.authenticated = False
    return True, "ログアウトしました"

def is_authenticated():
    """認証状態の確認"""
    return st.session_state.authenticated
