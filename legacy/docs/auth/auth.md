# 認証システム

## 概要

- **ソースファイル**: `auth/auth.py`（ロジック）、`auth/pages.py`（UI）
- **ハッシュアルゴリズム**: pbkdf2_sha256（passlib ライブラリ）
- **セッション管理**: Streamlit `session_state`

## パスワードハッシュ

### hash_password(password) — `auth/auth.py:5`

```python
from passlib.hash import pbkdf2_sha256

def hash_password(password):
    return pbkdf2_sha256.hash(password)
```

- passlib の `pbkdf2_sha256.hash()` を使用
- ソルトの生成・付与は passlib が自動的に処理
- 生成されるハッシュ文字列の形式: `$pbkdf2-sha256$rounds$salt$hash`

### verify_password(password, hash) — `auth/auth.py:9`

```python
def verify_password(password, hash):
    return pbkdf2_sha256.verify(password, hash)
```

- 平文パスワードと保存されたハッシュを照合
- 戻り値: `True`（一致）/ `False`（不一致）

## ユーザー登録フロー (F-AUTH-01)

### register_user(username, password, test_mode=False) — `auth/auth.py:13`

```
入力: username, password
  │
  ├─ DB接続取得
  │
  ├─ ユーザー名重複チェック
  │  SELECT * FROM users WHERE username = ?
  │  │
  │  ├─ 重複あり → return (False, "このユーザー名は既に使用されています")
  │  └─ 重複なし → 続行
  │
  ├─ パスワードハッシュ化
  │  hash_password(password)
  │
  ├─ DBにINSERT
  │  INSERT INTO users (username, password) VALUES (?, ?)
  │  │
  │  ├─ 成功 → return (True, "ユーザー登録が完了しました")
  │  └─ 例外 → return (False, "登録エラー: {エラー詳細}")
  │
  └─ DB接続クローズ（test_mode=Falseの場合）
```

**戻り値**: `(bool, str)` — (成否, メッセージ)

### UI側の登録フロー — `auth/pages.py:register_form()`

```
フォーム送信
  │
  ├─ バリデーション
  │  ├─ ユーザー名 or パスワードが空 → "ユーザー名とパスワードは必須です"
  │  ├─ パスワード != 確認パスワード → "パスワードが一致しません"
  │  └─ len(password) < 6 → "パスワードは6文字以上にしてください"
  │
  ├─ register_user() 呼び出し
  │  │
  │  ├─ 成功
  │  │  ├─ st.success(message)
  │  │  ├─ login_user(username, password)  ← 自動ログイン
  │  │  └─ st.rerun()
  │  │
  │  └─ 失敗 → st.error(message)
```

## ログインフロー (F-AUTH-02)

### login_user(username, password) — `auth/auth.py:47`

```
入力: username, password
  │
  ├─ DB接続取得
  │
  ├─ ユーザー検索
  │  SELECT * FROM users WHERE username = ?
  │  │
  │  ├─ ユーザーなし → return (False, "ユーザー名が見つかりません")
  │  └─ ユーザーあり → 続行
  │
  ├─ パスワード検証
  │  verify_password(password, user['password'])
  │  │
  │  ├─ 一致
  │  │  ├─ session_state.user_id = user['id']
  │  │  ├─ session_state.username = user['username']
  │  │  ├─ session_state.authenticated = True
  │  │  └─ return (True, "ログインに成功しました")
  │  │
  │  └─ 不一致 → return (False, "パスワードが正しくありません")
  │
  └─ DB接続クローズ
```

**戻り値**: `(bool, str)` — (成否, メッセージ)

**注意**: `login_user()` には `test_mode` パラメータがない。`register_user()` と異なり、常にDB接続を閉じる。

### UI側のログインフロー — `auth/pages.py:login_form()`

```
フォーム送信
  │
  ├─ バリデーション
  │  └─ ユーザー名 or パスワードが空 → "ユーザー名とパスワードを入力してください"
  │
  ├─ login_user() 呼び出し
  │  │
  │  ├─ 成功 → st.success(message) → st.rerun()
  │  └─ 失敗 → st.error(message)
```

## ログアウトフロー (F-AUTH-03)

### logout_user() — `auth/auth.py:72`

```python
def logout_user():
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.authenticated = False
    return True, "ログアウトしました"
```

- DB操作なし（セッション状態のリセットのみ）
- 常に成功を返す

### UI側のログアウトフロー — `auth/pages.py:show_logout_ui()`

```
サイドバーに表示:
  - "ログイン中: {username}" テキスト
  - "ログアウト" ボタン
    │
    └─ クリック時
       ├─ logout_user() 呼び出し
       ├─ st.sidebar.success(message)
       └─ st.rerun()
```

## 認証状態確認 (F-AUTH-04)

### is_authenticated() — `auth/auth.py:79`

```python
def is_authenticated():
    return st.session_state.authenticated
```

- `session_state.authenticated` の値をそのまま返す
- `auth/pages.py:auth_page()` で使用され、認証済みの場合はログアウトUIを、未認証の場合はログイン/登録UIを表示

## セッション管理

### セッション変数

| 変数名 | 型 | 初期値 | 設定タイミング |
|---|---|---|---|
| `user_id` | `int` / `None` | `None` | ログイン成功時にユーザーIDをセット、ログアウト時にNullに |
| `username` | `str` / `None` | `None` | ログイン成功時にユーザー名をセット、ログアウト時にNullに |
| `authenticated` | `bool` | `False` | ログイン成功時に`True`、ログアウト時に`False` |

### セッションのライフサイクル

1. `init_session_state()` でデフォルト値を設定（アプリ起動時）
2. ログイン成功時に `login_user()` がセッション変数を更新
3. `app.py:main()` で `session_state.authenticated` を参照してページルーティング
4. ログアウト時に `logout_user()` がセッション変数をリセット

## セキュリティ考慮事項

### 現在の実装

- **パスワード保存**: pbkdf2_sha256でハッシュ化（ソルト付き）。平文保存は行っていない
- **認証状態**: サーバーサイドのsession_stateで管理（クライアントでの改ざん不可）
- **SQLインジェクション対策**: パラメータ化クエリ（プレースホルダ `?`）を使用
- **エラーメッセージ**: ユーザー名の存在有無とパスワードの誤りを別メッセージで返している

### 懸念点

- **ユーザー名列挙**: ログイン時のエラーメッセージが「ユーザー名が見つかりません」と「パスワードが正しくありません」で異なるため、ユーザー名の存在を確認可能
- **セッションタイムアウト**: タイムアウトの仕組みがなく、ブラウザを閉じるまでセッションが維持される
- **ブルートフォース対策**: ログイン試行回数の制限がない
- **パスワードポリシー**: 最小6文字のみ。大文字・小文字・記号の要件なし
- **登録時のエラー情報漏洩**: 例外メッセージがそのままユーザーに表示される（`f"登録エラー: {str(e)}"`）

---
