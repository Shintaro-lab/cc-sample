import streamlit as st
from auth.auth import register_user, login_user, logout_user, is_authenticated

def auth_page():
    """認証ページ（ログイン/登録）"""
    if is_authenticated():
        show_logout_ui()
    else:
        show_login_register_ui()

def show_login_register_ui():
    """ログイン/登録UI"""
    st.title("タスク管理アプリ")
    
    # タブでログインと登録を切り替え
    tab1, tab2 = st.tabs(["ログイン", "新規登録"])
    
    with tab1:
        st.header("ログイン")
        login_form()
    
    with tab2:
        st.header("アカウント登録")
        register_form()

def login_form():
    """ログインフォーム"""
    with st.form("login_form"):
        username = st.text_input("ユーザー名", key="login_username")
        password = st.text_input("パスワード", type="password", key="login_password")
        
        submit = st.form_submit_button("ログイン")
        
        if submit:
            if not username or not password:
                st.error("ユーザー名とパスワードを入力してください")
            else:
                success, message = login_user(username, password)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

def register_form():
    """アカウント登録フォーム"""
    with st.form("register_form"):
        username = st.text_input("ユーザー名", key="register_username")
        password = st.text_input("パスワード", type="password", key="register_password")
        confirm_password = st.text_input("パスワード（確認）", type="password", key="confirm_password")
        
        submit = st.form_submit_button("登録")
        
        if submit:
            if not username or not password:
                st.error("ユーザー名とパスワードは必須です")
            elif password != confirm_password:
                st.error("パスワードが一致しません")
            elif len(password) < 6:
                st.error("パスワードは6文字以上にしてください")
            else:
                success, message = register_user(username, password)
                if success:
                    st.success(message)
                    # 登録成功したら自動的にログイン
                    login_user(username, password)
                    st.rerun()
                else:
                    st.error(message)

def show_logout_ui():
    """ログアウトボタンの表示"""
    st.sidebar.write(f"ログイン中: {st.session_state.username}")
    
    if st.sidebar.button("ログアウト"):
        success, message = logout_user()
        if success:
            st.sidebar.success(message)
            st.rerun()
