# レガシーアプリ仕様ドキュメント

Streamlit製タスク管理アプリ（`../src/app/`）の仕様をドキュメント化したものです。
モダナイズプロジェクトの参考資料として使用します。

## 目次

### 概要レベル

| ドキュメント | 内容 |
|---|---|
| [システムアーキテクチャ](overview/architecture.md) | 技術スタック、ディレクトリ構成、モジュール依存関係、アプリ起動フロー、既知の制約 |
| [機能一覧](overview/feature-list.md) | 機能ID付き一覧表（F-AUTH / F-TASK / F-UI）、入出力・バリデーションルール、ステータス/優先度の定義値 |

### 詳細レベル

| ドキュメント | 内容 |
|---|---|
| [画面仕様](detail/screen-spec.md) | 全画面のレイアウト・コンポーネント・バリデーション・画面遷移図 |
| [認証システム](detail/auth.md) | pbkdf2_sha256によるハッシュ、登録/ログイン/ログアウトの詳細フロー、セキュリティ考慮事項 |
| [タスク管理ロジック](detail/task-management.md) | タスクデータモデル、CRUD各関数の仕様、フィルタリング・ソート・統計ロジック、test_modeパラメータ |
| [データベース設計](detail/database.md) | ER図、テーブル定義（CREATE TABLE文）、全SQLクエリ一覧、接続管理方式、データ整合性の懸念 |
| [実行環境・インフラストラクチャ](detail/infrastructure.md) | 依存パッケージ、Streamlit設定、テーマシステム、セッション状態変数一覧、テスト基盤 |

## ソースファイル対応表

| ソースファイル | 主な参照先ドキュメント |
|---|---|
| `app.py` | [アーキテクチャ](overview/architecture.md)、[画面仕様](detail/screen-spec.md) |
| `auth/auth.py` | [認証システム](detail/auth.md) |
| `auth/pages.py` | [画面仕様](detail/screen-spec.md)、[機能一覧](overview/feature-list.md) |
| `tasks/task_manager.py` | [タスク管理ロジック](detail/task-management.md) |
| `tasks/pages.py` | [画面仕様](detail/screen-spec.md)、[機能一覧](overview/feature-list.md) |
| `utils/db.py` | [データベース設計](detail/database.md) |
| `utils/theme.py` | [インフラストラクチャ](detail/infrastructure.md) |
| `.streamlit/config.toml` | [インフラストラクチャ](detail/infrastructure.md) |

## 機能ID索引

各詳細ドキュメントで参照される機能IDの定義は[機能一覧](overview/feature-list.md)を参照。

| 機能ID | 機能名 | 詳細ドキュメント |
|---|---|---|
| F-AUTH-01 | ユーザー登録 | [認証システム](detail/auth.md) |
| F-AUTH-02 | ログイン | [認証システム](detail/auth.md) |
| F-AUTH-03 | ログアウト | [認証システム](detail/auth.md) |
| F-AUTH-04 | 認証状態確認 | [認証システム](detail/auth.md) |
| F-AUTH-05 | パスワードハッシュ化 | [認証システム](detail/auth.md) |
| F-AUTH-06 | 登録後自動ログイン | [認証システム](detail/auth.md) |
| F-TASK-01 | タスク追加 | [タスク管理ロジック](detail/task-management.md) |
| F-TASK-02 | タスク一覧表示 | [タスク管理ロジック](detail/task-management.md) |
| F-TASK-03 | タスク編集 | [タスク管理ロジック](detail/task-management.md) |
| F-TASK-04 | タスク削除 | [タスク管理ロジック](detail/task-management.md) |
| F-TASK-05 | タスク完了 | [タスク管理ロジック](detail/task-management.md) |
| F-TASK-06 | タスクフィルタリング | [タスク管理ロジック](detail/task-management.md) |
| F-TASK-07 | タスク統計 | [タスク管理ロジック](detail/task-management.md) |
| F-TASK-08 | カテゴリ一覧取得 | [タスク管理ロジック](detail/task-management.md) |
| F-TASK-09 | 期限切れ警告 | [画面仕様](detail/screen-spec.md) |
| F-UI-01 | テーマ切替 | [インフラストラクチャ](detail/infrastructure.md) |
| F-UI-02 | ページルーティング | [アーキテクチャ](overview/architecture.md) |
| F-UI-03 | ステータス表示名変換 | [機能一覧](overview/feature-list.md) |
| F-UI-04 | 優先度表示名変換 | [機能一覧](overview/feature-list.md) |
