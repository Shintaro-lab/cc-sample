# 機能一覧

## 認証機能 (F-AUTH)

| 機能ID | 機能名 | 説明 | ソース |
|---|---|---|---|
| F-AUTH-01 | ユーザー登録 | 新規ユーザーアカウントの作成 | `auth/auth.py:register_user()`, `auth/pages.py:register_form()` |
| F-AUTH-02 | ログイン | ユーザー名とパスワードによる認証 | `auth/auth.py:login_user()`, `auth/pages.py:login_form()` |
| F-AUTH-03 | ログアウト | セッションのクリアによるログアウト | `auth/auth.py:logout_user()`, `auth/pages.py:show_logout_ui()` |
| F-AUTH-04 | 認証状態確認 | セッションに基づく認証状態チェック | `auth/auth.py:is_authenticated()` |
| F-AUTH-05 | パスワードハッシュ化 | pbkdf2_sha256によるパスワード保護 | `auth/auth.py:hash_password()` |
| F-AUTH-06 | 登録後自動ログイン | 登録成功時に自動的にログイン処理を実行 | `auth/pages.py:register_form()` |

### F-AUTH-01: ユーザー登録

- **入力**: ユーザー名、パスワード、パスワード（確認）
- **バリデーションルール**:
  - ユーザー名: 必須
  - パスワード: 必須、6文字以上
  - パスワード確認: パスワードと一致すること
  - ユーザー名の重複不可（DBのUNIQUE制約）
- **出力**: 成功メッセージまたはエラーメッセージ
- **副作用**: usersテーブルにレコード挿入、自動ログイン（F-AUTH-06）

### F-AUTH-02: ログイン

- **入力**: ユーザー名、パスワード
- **バリデーションルール**:
  - ユーザー名: 必須
  - パスワード: 必須
  - ユーザー名が存在すること
  - パスワードがハッシュと一致すること
- **出力**: 成功メッセージまたはエラーメッセージ
- **副作用**: session_stateに `user_id`, `username`, `authenticated=True` をセット

### F-AUTH-03: ログアウト

- **入力**: なし（ボタンクリック）
- **出力**: 成功メッセージ
- **副作用**: session_stateの `user_id=None`, `username=None`, `authenticated=False` にリセット、ページ再描画

---

## タスク管理機能 (F-TASK)

| 機能ID | 機能名 | 説明 | ソース |
|---|---|---|---|
| F-TASK-01 | タスク追加 | 新規タスクの作成 | `tasks/task_manager.py:add_task()`, `tasks/pages.py:add_task_form()` |
| F-TASK-02 | タスク一覧表示 | フィルタリング済みタスクの一覧表示 | `tasks/task_manager.py:get_tasks()`, `tasks/pages.py:show_tasks()` |
| F-TASK-03 | タスク編集 | 既存タスクの更新 | `tasks/task_manager.py:update_task()`, `tasks/pages.py:edit_task_form()` |
| F-TASK-04 | タスク削除 | タスクの削除 | `tasks/task_manager.py:delete_task()`, `tasks/pages.py:show_task_card()` |
| F-TASK-05 | タスク完了 | ステータスを「完了」に変更 | `tasks/task_manager.py:update_task()`, `tasks/pages.py:show_task_card()` |
| F-TASK-06 | タスクフィルタリング | ステータス・優先度・カテゴリでのフィルター | `tasks/task_manager.py:get_tasks()`, `tasks/pages.py:task_filters()` |
| F-TASK-07 | タスク統計 | ステータス別・優先度別の集計表示 | `tasks/task_manager.py:get_task_stats()`, `tasks/pages.py:show_task_stats()` |
| F-TASK-08 | カテゴリ一覧取得 | ユーザーが使用中のカテゴリ取得 | `tasks/task_manager.py:get_task_categories()` |
| F-TASK-09 | 期限切れ警告 | 期限超過かつ未完了タスクに警告表示 | `tasks/pages.py:show_task_card()` |

### F-TASK-01: タスク追加

- **入力**: タイトル、説明、ステータス、優先度、カテゴリ、期限日
- **バリデーションルール**:
  - タイトル: 必須
  - ステータス: デフォルト `not_started`
  - 優先度: デフォルト `medium`
  - 期限日: `min_value=datetime.date.today()`（過去日付は選択不可）
- **出力**: 成功メッセージまたはエラーメッセージ
- **副作用**: tasksテーブルにレコード挿入、ページ再描画

### F-TASK-02: タスク一覧表示

- **入力**: フィルター条件（session_stateから取得）
- **ソート順**: 期限日昇順（NULLは末尾）、同一期限日の場合は作成日降順
- **出力**: タスクカードの一覧、タスクがない場合は「表示するタスクがありません」

### F-TASK-03: タスク編集

- **入力**: タイトル、説明、ステータス、優先度、カテゴリ、期限日
- **バリデーションルール**:
  - タイトル: 必須
  - 期限日: `min_value=None`（過去の日付も許可）
- **出力**: 成功メッセージまたはエラーメッセージ
- **副作用**: tasksテーブルのレコード更新、editing_task状態のクリア、ページ再描画

### F-TASK-06: タスクフィルタリング

- **フィルター項目**:
  - ステータス: すべて / 未着手 / 進行中 / 完了
  - 優先度: すべて / 低 / 中 / 高
  - カテゴリ: すべて / （ユーザーの既存カテゴリ一覧から動的生成）
- **フィルター条件**: AND結合（複数条件指定時はすべて満たすもの）

### F-TASK-07: タスク統計

- **表示項目**:
  - 合計タスク数
  - ステータス別: 件数とパーセンテージ
  - 優先度別: 件数とパーセンテージ
- **パーセンテージ計算**: `int(count / total * 100)` （小数点以下切り捨て）

---

## UI機能 (F-UI)

| 機能ID | 機能名 | 説明 | ソース |
|---|---|---|---|
| F-UI-01 | テーマ切替 | ライト/ダークモードの切替 | `utils/theme.py:switch_theme()`, `app.py` |
| F-UI-02 | ページルーティング | 認証状態に基づく画面切替 | `app.py:main()` |
| F-UI-03 | ステータス表示名変換 | 内部値を日本語表示名に変換 | `tasks/pages.py:format_status()` |
| F-UI-04 | 優先度表示名変換 | 内部値を日本語表示名に変換 | `tasks/pages.py:format_priority()` |

---

## データ定義値

### ステータス (status)

| 内部値 | 表示名 | アイコン |
|---|---|---|
| `not_started` | 未着手 | 🔴 |
| `in_progress` | 進行中 | 🟠 |
| `completed` | 完了 | 🟢 |

- デフォルト値: `not_started`（DB定義）、追加フォームの初期選択: `not_started`（index=0）

### 優先度 (priority)

| 内部値 | 表示名 | アイコン |
|---|---|---|
| `low` | 低 | 🔽 |
| `medium` | 中 | ➖ |
| `high` | 高 | 🔼 |

- デフォルト値: `medium`（DB定義）、追加フォームの初期選択: `medium`（index=1）

### テーマモード (theme_mode)

| 内部値 | 表示名 |
|---|---|
| `light` | ライト |
| `dark` | ダーク |

- デフォルト値: `light`
