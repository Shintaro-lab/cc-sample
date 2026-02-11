# システムアーキテクチャ

## 技術スタック

| カテゴリ | 技術 | バージョン/備考 |
|---|---|---|
| フレームワーク | Streamlit | Webアプリケーションフレームワーク |
| 言語 | Python | 3.x |
| データベース | SQLite3 | ファイルベースRDB（Python標準ライブラリ） |
| 認証ライブラリ | passlib (pbkdf2_sha256) | パスワードハッシュ化 |
| 状態管理 | Streamlit session_state | サーバーサイドセッション |

## ディレクトリ構成

```
legacy/src/app/
├── .streamlit/
│   └── config.toml          # Streamlit設定（ツールバー・UIカスタマイズ）
├── app.py                   # アプリケーションエントリーポイント
├── auth/
│   ├── __init__.py
│   ├── auth.py              # 認証ロジック（ハッシュ・ユーザー管理）
│   └── pages.py             # 認証画面UI（ログイン・登録・ログアウト）
├── tasks/
│   ├── __init__.py
│   ├── pages.py             # タスク管理画面UI（一覧・追加・編集・フィルター・統計）
│   └── task_manager.py      # タスク管理ロジック（CRUD・フィルタリング・統計）
├── utils/
│   ├── __init__.py
│   ├── db.py                # DB接続管理・テーブル初期化・セッション状態初期化
│   └── theme.py             # テーマ切替（ライト/ダーク CSS注入）
└── data/
    ├── taskmanager.db        # 本番用SQLiteデータベースファイル
    └── test_taskmanager.db   # テスト用SQLiteデータベースファイル
```

## モジュール依存関係

```
app.py
├── utils.db        [init_db, init_session_state]
├── utils.theme     [switch_theme]
├── auth.pages      [auth_page]
└── tasks.pages     [tasks_page]

auth.pages
└── auth.auth       [register_user, login_user, logout_user, is_authenticated]

auth.auth
└── utils.db        [get_connection]

tasks.pages
└── tasks.task_manager  [add_task, get_tasks, get_task, update_task,
                         delete_task, get_task_categories, get_task_stats]

tasks.task_manager
└── utils.db        [get_connection]

utils.theme
└── (streamlitのみ)

utils.db
└── (標準ライブラリのみ: sqlite3, os, pathlib)
```

### 依存関係の特徴

- **utils層** は他のアプリケーションモジュールに依存しない（最下層）
- **auth.auth** と **tasks.task_manager** はビジネスロジック層で、utils.db のみに依存
- **auth.pages** と **tasks.pages** はUI層で、対応するビジネスロジックモジュールに依存
- **app.py** はエントリーポイントとして全モジュールを統合
- 循環依存は存在しない

## アプリケーション起動フロー

```
1. app.py が実行される
   │
2. session_state にテーマモード ("theme_mode") を初期化（デフォルト: "light"）
   │
3. st.set_page_config() でページ設定
   │  - page_title: "タスク管理アプリ"
   │  - page_icon: "✅"
   │  - layout: "wide"
   │
4. switch_theme() でテーマCSS注入
   │
5. init_session_state() でセッション変数を初期化
   │  - user_id: None
   │  - username: None
   │  - authenticated: False
   │
6. init_db() でデータベーステーブルを作成（IF NOT EXISTS）
   │  - users テーブル
   │  - tasks テーブル
   │
7. main() 関数の実行
   │
   ├─ サイドバー描画
   │  ├─ タイトル表示
   │  ├─ テーマ選択セレクトボックス
   │  └─ テーマ変更時: session_state更新 → switch_theme() → st.rerun()
   │
   └─ 認証状態による分岐
      ├─ authenticated == True  → tasks_page() を表示
      └─ authenticated == False → auth_page() を表示
```

## 既知の制約・設計上の特徴

### データベース
- SQLiteを使用しているため、同時接続数に制限がある
- 各関数呼び出しごとに接続を開き、処理後に閉じるパターン（コネクションプーリングなし）
- 外部キー制約は `FOREIGN KEY` で宣言されているが、SQLiteではデフォルトで強制されない（`PRAGMA foreign_keys = ON` の設定がない）

### 認証・セキュリティ
- セッション管理は Streamlit の `session_state` に完全に依存（サーバーサイド、ブラウザタブ単位）
- セッションタイムアウトの仕組みがない
- CSRF対策は Streamlit フレームワークに依存

### テーマ
- CSS を `st.markdown()` で直接注入する方式（`unsafe_allow_html=True`）
- Streamlit のネイティブテーマ設定ではなく、カスタムCSS上書きによる実装

### テストモード
- 環境変数 `TEST_MODE=1` で テスト用DBパスに切り替わる
- ビジネスロジック関数に `test_mode` パラメータがあり、`True` の場合DB接続を閉じない
