import streamlit as st
import datetime
from tasks.task_manager import (
    add_task, get_tasks, get_task, update_task, 
    delete_task, get_task_categories, get_task_stats
)

def tasks_page():
    """タスク管理のメインページ"""
    st.title("タスク管理")
    
    # サイドバーにタスク追加と統計情報
    with st.sidebar:
        st.header("タスク追加")
        add_task_form()
        
        st.markdown("---")
        show_task_stats()
    
    # メインエリアにタスク一覧とフィルター
    task_filters()
    show_tasks()

def add_task_form():
    """タスク追加フォーム"""
    with st.form("add_task_form"):
        title = st.text_input("タイトル*")
        description = st.text_area("説明")
        
        col1, col2 = st.columns(2)
        with col1:
            status = st.selectbox(
                "ステータス",
                options=["not_started", "in_progress", "completed"],
                format_func=format_status,
                index=0
            )
            
            category = st.text_input("カテゴリ")
        
        with col2:
            priority = st.selectbox(
                "優先度",
                options=["low", "medium", "high"],
                format_func=format_priority,
                index=1
            )
            
            due_date = st.date_input(
                "期限",
                value=None,
                min_value=datetime.date.today(),
                format="YYYY/MM/DD"
            )
            # Noneの場合の処理
            if due_date == datetime.date(1970, 1, 1):  # streamlitのデフォルト値
                due_date = None
        
        submit = st.form_submit_button("タスクを追加")
        
        if submit:
            if not title:
                st.error("タイトルは必須です")
            else:
                # 日付をSQL用の文字列形式に変換
                due_date_str = due_date.isoformat() if due_date else None
                
                success, message = add_task(
                    st.session_state.user_id,
                    title,
                    description,
                    status,
                    priority,
                    category,
                    due_date_str
                )
                
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

def task_filters():
    """タスクのフィルターUI"""
    st.subheader("タスクフィルター")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox(
            "ステータスでフィルター",
            options=["all", "not_started", "in_progress", "completed"],
            format_func=lambda x: "すべて" if x == "all" else format_status(x),
            key="status_filter"
        )
    
    with col2:
        priority_filter = st.selectbox(
            "優先度でフィルター",
            options=["all", "low", "medium", "high"],
            format_func=lambda x: "すべて" if x == "all" else format_priority(x),
            key="priority_filter"
        )
    
    with col3:
        # ユーザーのカテゴリ一覧を取得
        categories = get_task_categories(st.session_state.user_id)
        # "すべて"オプションを追加
        category_options = ["all"] + categories
        
        category_filter = st.selectbox(
            "カテゴリでフィルター",
            options=category_options,
            format_func=lambda x: "すべて" if x == "all" else x,
            key="category_filter"
        )
    
    # フィルター値をセッションに保存
    st.session_state.task_filters = {
        "status": None if status_filter == "all" else status_filter,
        "priority": None if priority_filter == "all" else priority_filter,
        "category": None if category_filter == "all" else category_filter
    }

def show_tasks():
    """タスク一覧の表示"""
    filters = getattr(st.session_state, "task_filters", {"status": None, "priority": None, "category": None})
    
    tasks = get_tasks(
        st.session_state.user_id,
        status=filters["status"],
        priority=filters["priority"],
        category=filters["category"]
    )
    
    if not tasks:
        st.info("表示するタスクがありません")
        return
    
    for task in tasks:
        show_task_card(task)

def show_task_card(task):
    """タスクカードの表示"""
    # ステータスに応じた色を設定
    status_colors = {
        "not_started": "🔴",
        "in_progress": "🟠",
        "completed": "🟢"
    }
    status_icon = status_colors.get(task["status"], "⚪")
    
    # 優先度に応じたアイコン
    priority_icons = {
        "low": "🔽",
        "medium": "➖",
        "high": "🔼"
    }
    priority_icon = priority_icons.get(task["priority"], "➖")
    
    # タスクカードのヘッダー
    card_header = f"{status_icon} {task['title']} {priority_icon}"
    if task["category"]:
        card_header += f" #{task['category']}"
    
    with st.expander(card_header):
        # タスク詳細を表示
        if task["description"]:
            st.markdown(f"**説明:** {task['description']}")
        
        # 期限日を表示（ある場合）
        if task["due_date"]:
            try:
                due_date = datetime.date.fromisoformat(task["due_date"])
                st.markdown(f"**期限:** {due_date.strftime('%Y/%m/%d')}")
                
                # 期限が過ぎている場合は警告
                if due_date < datetime.date.today() and task["status"] != "completed":
                    st.warning("期限が過ぎています")
            except ValueError:
                st.markdown(f"**期限:** {task['due_date']}")
        
        # アクションボタン
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if task["status"] != "completed":
                if st.button("完了", key=f"complete_{task['id']}"):
                    success, message = update_task(
                        task["id"], 
                        st.session_state.user_id,
                        status="completed"
                    )
                    if success:
                        st.success(message)
                        st.rerun()
        
        with col2:
            if st.button("編集", key=f"edit_{task['id']}"):
                st.session_state.editing_task = task
                st.rerun()
        
        with col3:
            if st.button("削除", key=f"delete_{task['id']}"):
                success, message = delete_task(task["id"], st.session_state.user_id)
                if success:
                    st.success(message)
                    st.rerun()
    
    # 編集中のタスクがこのタスクなら編集フォームを表示
    if hasattr(st.session_state, "editing_task") and st.session_state.editing_task["id"] == task["id"]:
        edit_task_form(task)

def edit_task_form(task):
    """タスク編集フォーム"""
    st.markdown("---")
    st.subheader(f"タスク編集: {task['title']}")
    
    with st.form(f"edit_task_form_{task['id']}"):
        title = st.text_input("タイトル*", value=task["title"])
        description = st.text_area("説明", value=task["description"] or "")
        
        col1, col2 = st.columns(2)
        with col1:
            status_options = ["not_started", "in_progress", "completed"]
            status_index = status_options.index(task["status"]) if task["status"] in status_options else 0
            
            status = st.selectbox(
                "ステータス",
                options=status_options,
                format_func=format_status,
                index=status_index
            )
            
            category = st.text_input("カテゴリ", value=task["category"] or "")
        
        with col2:
            priority_options = ["low", "medium", "high"]
            priority_index = priority_options.index(task["priority"]) if task["priority"] in priority_options else 1
            
            priority = st.selectbox(
                "優先度",
                options=priority_options,
                format_func=format_priority,
                index=priority_index
            )
            
            # 期限日の設定
            default_date = None
            if task["due_date"]:
                try:
                    default_date = datetime.date.fromisoformat(task["due_date"])
                except ValueError:
                    pass
            
            due_date = st.date_input(
                "期限",
                value=default_date,
                min_value=None,  # 過去の日付も許可
                format="YYYY/MM/DD"
            )
            # Noneの場合の処理
            if due_date == datetime.date(1970, 1, 1):  # streamlitのデフォルト値
                due_date = None
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("更新")
        with col2:
            cancel = st.form_submit_button("キャンセル")
        
        if submit:
            if not title:
                st.error("タイトルは必須です")
            else:
                # 日付をSQL用の文字列形式に変換
                due_date_str = due_date.isoformat() if due_date else None
                
                success, message = update_task(
                    task["id"],
                    st.session_state.user_id,
                    title,
                    description,
                    status,
                    priority,
                    category,
                    due_date_str
                )
                
                if success:
                    st.success(message)
                    # 編集モードを終了
                    if hasattr(st.session_state, "editing_task"):
                        del st.session_state.editing_task
                    st.rerun()
                else:
                    st.error(message)
        
        elif cancel:
            # 編集モードを終了
            if hasattr(st.session_state, "editing_task"):
                del st.session_state.editing_task
            st.rerun()

def show_task_stats():
    """タスク統計情報の表示"""
    stats = get_task_stats(st.session_state.user_id)
    
    st.subheader("タスク統計")
    
    total = stats.get('total', 0)
    if total == 0:
        st.info("タスクがありません")
        return
    
    st.write(f"合計タスク数: {total}")
    
    # ステータス別の統計
    status_stats = stats.get('status', {})
    st.write("ステータス別:")
    for status, count in status_stats.items():
        st.write(f"{format_status(status)}: {count} ({int(count/total*100)}%)")
    
    # 優先度別の統計
    priority_stats = stats.get('priority', {})
    st.write("優先度別:")
    for priority, count in priority_stats.items():
        st.write(f"{format_priority(priority)}: {count} ({int(count/total*100)}%)")

def format_status(status):
    """ステータスの表示名変換"""
    status_names = {
        "not_started": "未着手",
        "in_progress": "進行中",
        "completed": "完了"
    }
    return status_names.get(status, status)

def format_priority(priority):
    """優先度の表示名変換"""
    priority_names = {
        "low": "低",
        "medium": "中",
        "high": "高"
    }
    return priority_names.get(priority, priority)
