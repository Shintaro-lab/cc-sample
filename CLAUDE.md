# プロジェクト概要

Streamlitベースのタスク管理アプリケーション。レガシーアプリのリプレースを目的とする。

## フォルダ構成

```
cc-sample/
├── legacy/                          # レガシーアプリ
│   ├── docs/                        # 仕様ドキュメント
│   │   ├── README.md                # ドキュメント目次・機能ID索引
│   │   ├── shared/                  # 共通ドキュメント
│   │   │   ├── architecture.md      # アーキテクチャ・技術スタック
│   │   │   ├── feature-list.md      # 機能一覧（F-AUTH, F-TASK, F-UI）
│   │   │   ├── screen-spec.md       # 画面仕様・画面遷移
│   │   │   ├── database.md          # DB定義・ER図・SQL
│   │   │   └── infrastructure.md    # 依存パッケージ・テーマ・セッション
│   │   ├── auth/                    # 認証関連（仕様書 + E2Eテストケース）
│   │   │   └── auth.md              # 認証システム仕様
│   │   └── task-management/         # タスク管理関連（仕様書 + E2Eテストケース）
│   │       └── task-management.md   # タスク管理仕様
│   └── src/app/                     # ソースコード
│       ├── app.py                   # エントリポイント
│       ├── auth/                    # 認証モジュール
│       │   ├── auth.py              # 認証ロジック
│       │   └── pages.py            # 認証画面
│       ├── tasks/                   # タスク管理モジュール
│       │   ├── task_manager.py      # タスクCRUD
│       │   └── pages.py            # タスク管理画面
│       ├── utils/                   # ユーティリティ
│       │   ├── db.py               # DB接続管理
│       │   └── theme.py            # テーマ管理
│       └── data/                    # SQLiteデータファイル
├── docs/                            # プロジェクト共通ドキュメント
│   └── template/
│       └── e2e-test-case.md         # E2Eテストケース表テンプレート
└── .claude/
    └── skills/
        └── e2e-test-generator/      # E2Eテストケース生成スキル
```
