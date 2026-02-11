# データベース設計

## 概要

- **DBMS**: SQLite3（Python標準ライブラリ）
- **本番DBパス**: `data/taskmanager.db`（`legacy/src/app/` からの相対パス）
- **テスト用DBパス**: `app/data/test_taskmanager.db`（環境変数 `TEST_MODE=1` で切替）
- **ソースファイル**: `utils/db.py`

## ER図

```
+-------------------+          +----------------------------+
|      users        |          |          tasks             |
+-------------------+          +----------------------------+
| PK id       INT   |─────1:N─| PK id          INT         |
|    username  TEXT  |         |    user_id      INT (FK)   |
|    password  TEXT  |         |    title        TEXT        |
|    created_at TS   |         |    description  TEXT        |
+-------------------+          |    status       TEXT        |
                               |    priority     TEXT        |
                               |    category     TEXT        |
                               |    due_date     TEXT        |
                               |    created_at   TS          |
                               +----------------------------+
```

## テーブル定義

### users テーブル

```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

| カラム名 | 型 | 制約 | 説明 |
|---|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | ユーザーID |
| username | TEXT | UNIQUE NOT NULL | ユーザー名（重複不可） |
| password | TEXT | NOT NULL | pbkdf2_sha256ハッシュ済みパスワード |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 登録日時 |

### tasks テーブル

```sql
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
```

| カラム名 | 型 | 制約 | デフォルト値 | 説明 |
|---|---|---|---|---|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | - | タスクID |
| user_id | INTEGER | NOT NULL, FK→users(id) | - | 所有ユーザーのID |
| title | TEXT | NOT NULL | - | タスクタイトル |
| description | TEXT | - | NULL | タスクの説明 |
| status | TEXT | - | `'not_started'` | ステータス（`not_started` / `in_progress` / `completed`） |
| priority | TEXT | - | `'medium'` | 優先度（`low` / `medium` / `high`） |
| category | TEXT | - | NULL | カテゴリ（自由入力） |
| due_date | TEXT | - | NULL | 期限日（ISO 8601形式: `YYYY-MM-DD`） |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | - | 作成日時 |

## 接続管理

### get_connection() — `utils/db.py:12`

```python
def get_connection():
    if os.environ.get("TEST_MODE") == "1":
        db_path = TEST_DB_PATH  # Path("app/data/test_taskmanager.db")
    else:
        db_path = DB_PATH       # Path("data/taskmanager.db")

    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn
```

**接続パターン**:
- 各関数呼び出しごとに `get_connection()` で新しい接続を取得
- 処理完了後に `conn.close()` で接続を閉じる
- `test_mode=True` の場合は接続を閉じない（テスト時のトランザクション管理用）
- `row_factory = sqlite3.Row` により、結果は辞書ライクなRowオブジェクトとして返される
- DBファイルの親ディレクトリが存在しない場合は自動作成（`os.makedirs`）

## SQLクエリパターン一覧

### users テーブル操作

| 操作 | クエリ | 使用箇所 |
|---|---|---|
| ユーザー名重複チェック | `SELECT * FROM users WHERE username = ?` | `auth/auth.py:register_user()` |
| ユーザー登録 | `INSERT INTO users (username, password) VALUES (?, ?)` | `auth/auth.py:register_user()` |
| ユーザー検索（ログイン） | `SELECT * FROM users WHERE username = ?` | `auth/auth.py:login_user()` |

### tasks テーブル操作

| 操作 | クエリ | 使用箇所 |
|---|---|---|
| タスク追加 | `INSERT INTO tasks (user_id, title, description, status, priority, category, due_date) VALUES (?, ?, ?, ?, ?, ?, ?)` | `tasks/task_manager.py:add_task()` |
| タスク一覧取得 | `SELECT * FROM tasks WHERE user_id = ? [AND status = ?] [AND priority = ?] [AND category = ?] ORDER BY CASE WHEN due_date IS NULL THEN 1 ELSE 0 END, due_date, created_at DESC` | `tasks/task_manager.py:get_tasks()` |
| タスク詳細取得 | `SELECT * FROM tasks WHERE id = ? AND user_id = ?` | `tasks/task_manager.py:get_task()` |
| タスク更新 | `UPDATE tasks SET {動的フィールド} WHERE id = ? AND user_id = ?` | `tasks/task_manager.py:update_task()` |
| タスク削除 | `DELETE FROM tasks WHERE id = ? AND user_id = ?` | `tasks/task_manager.py:delete_task()` |
| カテゴリ一覧 | `SELECT DISTINCT category FROM tasks WHERE user_id = ? AND category IS NOT NULL` | `tasks/task_manager.py:get_task_categories()` |
| ステータス別集計 | `SELECT status, COUNT(*) as count FROM tasks WHERE user_id = ? GROUP BY status` | `tasks/task_manager.py:get_task_stats()` |
| 優先度別集計 | `SELECT priority, COUNT(*) as count FROM tasks WHERE user_id = ? GROUP BY priority` | `tasks/task_manager.py:get_task_stats()` |

### ソート順序の詳細

`get_tasks()` のORDER BY句:
```sql
ORDER BY
  CASE WHEN due_date IS NULL THEN 1 ELSE 0 END,  -- NULLを末尾に配置
  due_date,                                        -- 期限日昇順
  created_at DESC                                  -- 同一期限日の場合は作成日降順
```

### 動的UPDATE文の構築

`update_task()` では、`None` でないパラメータのみをUPDATE文に含める動的クエリ構築を行う:

```python
update_fields = []
params = []
if title is not None:
    update_fields.append("title = ?")
    params.append(title)
# ... 他のフィールドも同様
query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = ? AND user_id = ?"
```

## データ整合性に関する懸念

### 外部キー制約の未強制

- `tasks.user_id` に `FOREIGN KEY (user_id) REFERENCES users (id)` が宣言されているが、SQLiteではデフォルトで外部キー制約が強制されない
- `PRAGMA foreign_keys = ON` の実行がないため、存在しない `user_id` でもタスクを挿入可能
- ユーザー削除時にタスクが孤児レコードになるリスクがある（ただし、ユーザー削除機能は未実装）

### status/priority の値制約なし

- `status` と `priority` はTEXT型でCHECK制約がなく、アプリケーション側でのみ値が制限されている
- 直接DBを操作した場合に不正な値が入る可能性がある

### トランザクション管理

- 各操作は単一のINSERT/UPDATE/DELETEで完結しており、複数テーブルにまたがるトランザクションは存在しない
- `register_user()` では重複チェック(SELECT)と登録(INSERT)の間にレースコンディションが発生する可能性がある（USERテーブルのUNIQUE制約で保護されるが、例外ハンドリングが汎用的）

### インデックス

- 明示的なインデックス作成がない（PRIMARY KEYとUNIQUEによる暗黙のインデックスのみ）
- `tasks.user_id` にインデックスがないため、タスク数が増加した場合にクエリパフォーマンスが劣化する可能性がある

---

