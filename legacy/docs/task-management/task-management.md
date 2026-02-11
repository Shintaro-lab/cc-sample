# タスク管理ロジック

## 概要

- **ソースファイル**: `tasks/task_manager.py`（ロジック）、`tasks/pages.py`（UI）
- **機能**: タスクのCRUD操作、フィルタリング、ソート、統計情報取得
- **データストア**: SQLite（`utils/db.py` 経由）

## タスクデータモデル

| フィールド | 型 | 必須 | デフォルト | 説明 |
|---|---|---|---|---|
| id | INTEGER | 自動 | AUTOINCREMENT | タスクID（主キー） |
| user_id | INTEGER | Yes | - | 所有ユーザーID |
| title | TEXT | Yes | - | タスクタイトル |
| description | TEXT | No | NULL | タスクの説明 |
| status | TEXT | No | `'not_started'` | ステータス |
| priority | TEXT | No | `'medium'` | 優先度 |
| category | TEXT | No | NULL | カテゴリ（自由入力） |
| due_date | TEXT | No | NULL | 期限日（ISO 8601: `YYYY-MM-DD`） |
| created_at | TIMESTAMP | 自動 | CURRENT_TIMESTAMP | 作成日時 |

## CRUD操作

### Create: add_task() — `tasks/task_manager.py:4`

```python
def add_task(user_id, title, description=None, status="not_started",
             priority="medium", category=None, due_date=None, test_mode=False)
```

**パラメータ**:

| パラメータ | 型 | デフォルト | 説明 |
|---|---|---|---|
| user_id | int | (必須) | ユーザーID |
| title | str | (必須) | タスクタイトル |
| description | str/None | None | タスクの説明 |
| status | str | `"not_started"` | ステータス |
| priority | str | `"medium"` | 優先度 |
| category | str/None | None | カテゴリ |
| due_date | str/None | None | 期限日（ISO 8601形式の文字列） |
| test_mode | bool | False | テストモード |

**戻り値**: `(bool, str)` — (成否, メッセージ)

**実行SQL**:
```sql
INSERT INTO tasks (user_id, title, description, status, priority, category, due_date)
VALUES (?, ?, ?, ?, ?, ?, ?)
```

**UI側の処理** (`tasks/pages.py:add_task_form()`):
- 期限日は `datetime.date` オブジェクトから `isoformat()` で文字列に変換
- `min_value=datetime.date.today()` により過去日付は選択不可
- Streamlitの `date_input` がデフォルトで `datetime.date(1970, 1, 1)` を返す場合はNullとして扱う

---

### Read: get_tasks() — `tasks/task_manager.py:38`

```python
def get_tasks(user_id, status=None, priority=None, category=None, test_mode=False)
```

**パラメータ**:

| パラメータ | 型 | デフォルト | 説明 |
|---|---|---|---|
| user_id | int | (必須) | ユーザーID |
| status | str/None | None | ステータスフィルター |
| priority | str/None | None | 優先度フィルター |
| category | str/None | None | カテゴリフィルター |
| test_mode | bool | False | テストモード |

**戻り値**: `list[sqlite3.Row]` — タスクのリスト

**クエリ構築ロジック**:
```python
query = "SELECT * FROM tasks WHERE user_id = ?"
params = [user_id]

if status:
    query += " AND status = ?"
    params.append(status)
if priority:
    query += " AND priority = ?"
    params.append(priority)
if category:
    query += " AND category = ?"
    params.append(category)

query += " ORDER BY CASE WHEN due_date IS NULL THEN 1 ELSE 0 END, due_date, created_at DESC"
```

**フィルタリング条件**: AND結合（指定されたフィルターをすべて満たすタスクのみ取得）

**ソート順序**:
1. 期限日がNULLのものは末尾
2. 期限日昇順（近い順）
3. 同一期限日の場合は作成日降順（新しい順）

---

### Read (単一): get_task() — `tasks/task_manager.py:75`

```python
def get_task(task_id, user_id, test_mode=False)
```

**パラメータ**:

| パラメータ | 型 | デフォルト | 説明 |
|---|---|---|---|
| task_id | int | (必須) | タスクID |
| user_id | int | (必須) | ユーザーID |
| test_mode | bool | False | テストモード |

**戻り値**: `sqlite3.Row / None` — タスクデータ or None

**実行SQL**:
```sql
SELECT * FROM tasks WHERE id = ? AND user_id = ?
```

**注意**: `user_id` も条件に含めることで、他ユーザーのタスクへのアクセスを防止している。

---

### Update: update_task() — `tasks/task_manager.py:96`

```python
def update_task(task_id, user_id, title=None, description=None,
                status=None, priority=None, category=None, due_date=None, test_mode=False)
```

**パラメータ**:

| パラメータ | 型 | デフォルト | 説明 |
|---|---|---|---|
| task_id | int | (必須) | タスクID |
| user_id | int | (必須) | ユーザーID |
| title | str/None | None | 更新するタイトル |
| description | str/None | None | 更新する説明 |
| status | str/None | None | 更新するステータス |
| priority | str/None | None | 更新する優先度 |
| category | str/None | None | 更新するカテゴリ |
| due_date | str/None | None | 更新する期限日 |
| test_mode | bool | False | テストモード |

**戻り値**: `(bool, str)` — (成否, メッセージ)

**動的UPDATE文構築**:
- `None` でないパラメータのみがSET句に含まれる
- すべてのパラメータが `None` の場合: `(False, "更新するフィールドが指定されていません")`

**UI側の呼び出し** (`tasks/pages.py:edit_task_form()`):
- 編集フォームではすべてのフィールドを位置引数として渡している（キーワード引数ではない）
- 「完了」ボタンからは `status="completed"` のみをキーワード引数で渡す

---

### Delete: delete_task() — `tasks/task_manager.py:157`

```python
def delete_task(task_id, user_id, test_mode=False)
```

**パラメータ**:

| パラメータ | 型 | デフォルト | 説明 |
|---|---|---|---|
| task_id | int | (必須) | タスクID |
| user_id | int | (必須) | ユーザーID |
| test_mode | bool | False | テストモード |

**戻り値**: `(bool, str)` — (成否, メッセージ)

**実行SQL**:
```sql
DELETE FROM tasks WHERE id = ? AND user_id = ?
```

**注意**: 削除確認ダイアログは実装されていない。ボタンクリックで即座に削除が実行される。

## カテゴリ管理

### get_task_categories() — `tasks/task_manager.py:182`

```python
def get_task_categories(user_id, test_mode=False)
```

**戻り値**: `list[str]` — カテゴリ文字列のリスト

**実行SQL**:
```sql
SELECT DISTINCT category FROM tasks WHERE user_id = ? AND category IS NOT NULL
```

- カテゴリはタスク追加時の自由入力テキストから動的に収集される
- マスターテーブルは存在しない
- NULLのカテゴリは除外される

## 統計情報

### get_task_stats() — `tasks/task_manager.py:202`

```python
def get_task_stats(user_id, test_mode=False)
```

**戻り値**: `dict` — 以下の構造

```python
{
    'status': {
        'not_started': int,  # 未着手の件数
        'in_progress': int,  # 進行中の件数
        'completed': int     # 完了の件数
    },
    'priority': {
        'low': int,          # 低優先度の件数
        'medium': int,       # 中優先度の件数
        'high': int          # 高優先度の件数
    },
    'total': int             # 合計タスク数（statusの件数合計）
}
```

**注意**: 実際の戻り値にはデータが存在するキーのみが含まれる（例: 未着手タスクがない場合、`'not_started'` キーは含まれない）。

**UI側の表示** (`tasks/pages.py:show_task_stats()`):
- 合計タスク数が0の場合は「タスクがありません」を表示
- パーセンテージは `int(count / total * 100)` で算出（小数点以下切り捨て）

## test_mode パラメータ

ビジネスロジック関数の多くに `test_mode` パラメータが存在する。

| 関数 | test_mode対応 |
|---|---|
| `add_task()` | あり |
| `get_tasks()` | あり |
| `get_task()` | あり |
| `update_task()` | あり |
| `delete_task()` | あり |
| `get_task_categories()` | あり |
| `get_task_stats()` | あり |
| `register_user()` | あり |
| `login_user()` | **なし** |
| `logout_user()` | **なし**（DB操作なし） |

**動作**: `test_mode=True` の場合、関数終了時にDB接続を `conn.close()` しない。これにより、テストコードで同一トランザクション内の操作をまとめて検証できる。

---