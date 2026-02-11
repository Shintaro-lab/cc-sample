import streamlit as st
from utils.db import init_db, init_session_state
from utils.theme import switch_theme
from auth.pages import auth_page
from tasks.pages import tasks_page

# セッション状態の初期化（テーマモード）
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "light"

# アプリのタイトルとアイコン
st.set_page_config(
    page_title="タスク管理アプリ",
    page_icon="✅",
    layout="wide"
)

# テーマの初期設定
switch_theme(st.session_state.theme_mode)

# セッション状態の初期化
init_session_state()

# データベースの初期化
init_db()

# メインアプリケーション
def main():
    """アプリケーションのメインエントリーポイント"""
    
    # サイドバーに基本情報を表示
    with st.sidebar:
        st.title("タスク管理アプリ")
        
        # テーマ選択
        theme_mode = st.selectbox(
            "配色モード",
            ["ライト", "ダーク"],
            index=0 if st.session_state.theme_mode == "light" else 1,
        )
        
        # テーマが変更された場合
        if theme_mode == "ライト" and st.session_state.theme_mode != "light":
            st.session_state.theme_mode = "light"
            switch_theme("light")
            st.rerun()
        elif theme_mode == "ダーク" and st.session_state.theme_mode != "dark":
            st.session_state.theme_mode = "dark"
            switch_theme("dark")
            st.rerun()
        
        st.markdown("---")
    
    # 認証状態に基づいて表示するページを決定
    if st.session_state.authenticated:
        # 認証済みユーザーにはタスク管理ページを表示
        tasks_page()
    else:
        # 未認証ユーザーには認証ページを表示
        auth_page()

if __name__ == "__main__":
    main()
