# 実行環境・インフラストラクチャ

## 依存パッケージ

| パッケージ | 用途 | 使用箇所 |
|---|---|---|
| streamlit | Webアプリケーションフレームワーク | 全モジュール |
| passlib | パスワードハッシュ化（pbkdf2_sha256） | `auth/auth.py` |
| sqlite3 | データベース（Python標準ライブラリ） | `utils/db.py` |
| os | ファイルパス操作、環境変数（Python標準ライブラリ） | `utils/db.py` |
| pathlib | パス管理（Python標準ライブラリ） | `utils/db.py` |
| datetime | 日付処理（Python標準ライブラリ） | `tasks/pages.py` |

## Streamlit設定

### .streamlit/config.toml

```toml
[client]
toolbarMode = "minimal"

[ui]
hideTopBar = true
```

| セクション | 設定 | 値 | 説明 |
|---|---|---|---|
| `[client]` | `toolbarMode` | `"minimal"` | ツールバーを最小表示モードに設定 |
| `[ui]` | `hideTopBar` | `true` | Streamlitのトップバーを非表示 |

### ページ設定 — `app.py:12`

```python
st.set_page_config(
    page_title="タスク管理アプリ",
    page_icon="✅",
    layout="wide"
)
```

| パラメータ | 値 | 説明 |
|---|---|---|
| `page_title` | `"タスク管理アプリ"` | ブラウザタブのタイトル |
| `page_icon` | `"✅"` | ブラウザタブのファビコン |
| `layout` | `"wide"` | ワイドレイアウト（デフォルトの中央寄せではなく全幅使用） |

## テーマシステム

### 概要 — `utils/theme.py`

CSS文字列を `st.markdown()` で注入する方式（`unsafe_allow_html=True`）。Streamlitのネイティブテーマ設定ではなく、カスタムCSSによるスタイル上書き。

### カラー定義

| プロパティ | ライトモード | ダークモード |
|---|---|---|
| `primaryColor` | `#FF4B4B` (赤) | `#FF6B6B` (薄赤) |
| `backgroundColor` | `#FFFFFF` (白) | `#1E1E1E` (濃灰) |
| `secondaryBackgroundColor` | `#F0F2F6` (薄灰) | `#121212` (ほぼ黒) |
| `textColor` | `#31333F` (濃灰) | `#FFFFFF` (白) |

### CSSターゲット

`switch_theme()` で注入されるCSSが適用されるセレクタ:

| CSSセレクタ | 適用対象 | 設定プロパティ |
|---|---|---|
| `.stApp` | アプリ全体 | `background-color`, `color` |
| `.stAppHeader` | アプリヘッダー | `background-color` |
| `.stSidebar` | サイドバー | `background-color`, `color` |
| `.stButton button` | ボタン | `color`, `background-color`, `border-color` |
| `.stFormSubmitButton button` | フォーム送信ボタン | `background-color`, `color`, `border-color` |
| `.stSelectbox` | セレクトボックス | `color` |
| `.stSelectbox label` | セレクトボックスラベル | `color` (with `!important`) |
| `.stTextInput` | テキスト入力 | `color` |
| `.stTextInput label` | テキスト入力ラベル | `color` (with `!important`) |
| `.stTabs [role=tablist] button` | タブボタン | `color` (with `!important`) |
| `.stHeader` | ヘッダー | `background-color`, `color` |

### テーマ切替フロー

```
1. ユーザーがサイドバーのセレクトボックスで配色モードを変更
   │
2. session_state.theme_mode を更新（"light" or "dark"）
   │
3. switch_theme(mode) を呼び出し
   │  - config辞書からモードに対応するカラーを取得
   │  - CSS文字列を生成
   │  - st.markdown() でHTMLとして注入
   │
4. st.rerun() でページ再描画
```

## セッション状態変数一覧

### 認証関連 — `utils/db.py:init_session_state()`

| 変数名 | 型 | 初期値 | 設定元 | 参照元 |
|---|---|---|---|---|
| `user_id` | `int/None` | `None` | `auth/auth.py:login_user()`, `logout_user()` | `tasks/pages.py` (各関数) |
| `username` | `str/None` | `None` | `auth/auth.py:login_user()`, `logout_user()` | `auth/pages.py:show_logout_ui()` |
| `authenticated` | `bool` | `False` | `auth/auth.py:login_user()`, `logout_user()` | `app.py:main()`, `auth/auth.py:is_authenticated()` |

### テーマ関連 — `app.py:8`

| 変数名 | 型 | 初期値 | 設定元 | 参照元 |
|---|---|---|---|---|
| `theme_mode` | `str` | `"light"` | `app.py:main()` (テーマ変更時) | `app.py` (テーマ適用・セレクトボックスindex) |

### タスク管理関連 — `tasks/pages.py`

| 変数名 | 型 | 初期値 | 設定元 | 参照元 |
|---|---|---|---|---|
| `task_filters` | `dict` | (未初期化) | `tasks/pages.py:task_filters()` | `tasks/pages.py:show_tasks()` |
| `editing_task` | `sqlite3.Row` | (未初期化) | `tasks/pages.py:show_task_card()` | `tasks/pages.py:show_task_card()`, `edit_task_form()` |

**注意**: `task_filters` と `editing_task` は `init_session_state()` で初期化されず、使用時に動的に作成される。`show_tasks()` では `getattr()` でデフォルト値付き参照、`show_task_card()` では `hasattr()` で存在チェックを行っている。

## テスト基盤

### テスト用DB

- **パス**: `app/data/test_taskmanager.db`（`utils/db.py:TEST_DB_PATH`）
- **切替方法**: 環境変数 `TEST_MODE=1` を設定
- `get_connection()` 内で `os.environ.get("TEST_MODE") == "1"` をチェック

### test_mode パラメータ

ビジネスロジック関数の `test_mode=True` パラメータにより、DB接続を閉じずに保持できる。テストコードでのトランザクション管理を想定した設計。

### テスト実装の現状

- テスト用のDBパスとtest_modeパラメータが用意されているが、テストコード自体は `legacy/src/app/` 配下に確認されていない
- テストフレームワーク（pytest等）の設定ファイルも未確認

---
