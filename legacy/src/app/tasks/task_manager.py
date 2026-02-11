from utils.db import get_connection
import streamlit as st

def add_task(user_id, title, description=None, status="not_started", 
             priority="medium", category=None, due_date=None, test_mode=False):
    """新しいタスクを追加
    
    Args:
        user_id: ユーザーID
        title: タスクのタイトル
        description: タスクの説明
        status: タスクの状態
        priority: 優先度
        category: カテゴリ
        due_date: 期限日
        test_mode: テストモード（Trueの場合、DB接続を閉じない）
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """
            INSERT INTO tasks (user_id, title, description, status, priority, category, due_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, title, description, status, priority, category, due_date)
        )
        conn.commit()
        if not test_mode:
            conn.close()
        return True, "タスクが追加されました"
    except Exception as e:
        if not test_mode:
            conn.close()
        return False, f"タスク追加エラー: {str(e)}"

def get_tasks(user_id, status=None, priority=None, category=None, test_mode=False):
    """ユーザーのタスクを取得（フィルタリングも可能）
    
    Args:
        user_id: ユーザーID
        status: フィルター（タスクの状態）
        priority: フィルター（優先度）
        category: フィルター（カテゴリ）
        test_mode: テストモード（Trueの場合、DB接続を閉じない）
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM tasks WHERE user_id = ?"
    params = [user_id]
    
    # フィルタリング条件を追加
    if status:
        query += " AND status = ?"
        params.append(status)
    if priority:
        query += " AND priority = ?"
        params.append(priority)
    if category:
        query += " AND category = ?"
        params.append(category)
    
    # 期限日でソート
    query += " ORDER BY CASE WHEN due_date IS NULL THEN 1 ELSE 0 END, due_date, created_at DESC"
    
    cursor.execute(query, params)
    tasks = cursor.fetchall()
    if not test_mode:
        conn.close()
    
    return tasks

def get_task(task_id, user_id, test_mode=False):
    """指定したタスクの詳細を取得
    
    Args:
        task_id: タスクID
        user_id: ユーザーID
        test_mode: テストモード（Trueの場合、DB接続を閉じない）
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, user_id)
    )
    task = cursor.fetchone()
    if not test_mode:
        conn.close()
    
    return task

def update_task(task_id, user_id, title=None, description=None, 
                status=None, priority=None, category=None, due_date=None, test_mode=False):
    """タスクを更新
    
    Args:
        task_id: タスクID
        user_id: ユーザーID
        title: タスクのタイトル
        description: タスクの説明
        status: タスクの状態
        priority: 優先度
        category: カテゴリ
        due_date: 期限日
        test_mode: テストモード（Trueの場合、DB接続を閉じない）
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # 更新するフィールドと値を準備
    update_fields = []
    params = []
    
    if title is not None:
        update_fields.append("title = ?")
        params.append(title)
    if description is not None:
        update_fields.append("description = ?")
        params.append(description)
    if status is not None:
        update_fields.append("status = ?")
        params.append(status)
    if priority is not None:
        update_fields.append("priority = ?")
        params.append(priority)
    if category is not None:
        update_fields.append("category = ?")
        params.append(category)
    if due_date is not None:
        update_fields.append("due_date = ?")
        params.append(due_date)
    
    if not update_fields:
        if not test_mode:
            conn.close()
        return False, "更新するフィールドが指定されていません"
    
    # クエリの作成
    query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = ? AND user_id = ?"
    params.extend([task_id, user_id])
    
    try:
        cursor.execute(query, params)
        conn.commit()
        if not test_mode:
            conn.close()
        return True, "タスクが更新されました"
    except Exception as e:
        if not test_mode:
            conn.close()
        return False, f"タスク更新エラー: {str(e)}"

def delete_task(task_id, user_id, test_mode=False):
    """タスクを削除
    
    Args:
        task_id: タスクID
        user_id: ユーザーID
        test_mode: テストモード（Trueの場合、DB接続を閉じない）
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "DELETE FROM tasks WHERE id = ? AND user_id = ?",
            (task_id, user_id)
        )
        conn.commit()
        if not test_mode:
            conn.close()
        return True, "タスクが削除されました"
    except Exception as e:
        if not test_mode:
            conn.close()
        return False, f"タスク削除エラー: {str(e)}"

def get_task_categories(user_id, test_mode=False):
    """ユーザーが使用しているタスクのカテゴリ一覧を取得
    
    Args:
        user_id: ユーザーID
        test_mode: テストモード（Trueの場合、DB接続を閉じない）
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT DISTINCT category FROM tasks WHERE user_id = ? AND category IS NOT NULL",
        (user_id,)
    )
    categories = [row['category'] for row in cursor.fetchall()]
    if not test_mode:
        conn.close()
    
    return categories

def get_task_stats(user_id, test_mode=False):
    """ユーザーのタスク統計情報を取得
    
    Args:
        user_id: ユーザーID
        test_mode: テストモード（Trueの場合、DB接続を閉じない）
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # ステータス別のタスク数
    cursor.execute(
        """
        SELECT status, COUNT(*) as count FROM tasks 
        WHERE user_id = ? 
        GROUP BY status
        """,
        (user_id,)
    )
    status_counts = {row['status']: row['count'] for row in cursor.fetchall()}
    
    # 優先度別のタスク数
    cursor.execute(
        """
        SELECT priority, COUNT(*) as count FROM tasks 
        WHERE user_id = ? 
        GROUP BY priority
        """,
        (user_id,)
    )
    priority_counts = {row['priority']: row['count'] for row in cursor.fetchall()}
    
    if not test_mode:
        conn.close()
    
    return {
        'status': status_counts,
        'priority': priority_counts,
        'total': sum(status_counts.values())
    }
