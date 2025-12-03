# タスク管理アプリ

Windowsデスクトップ上で動作するタスク管理ツールです。複数プロジェクトの管理、タスクの登録・進捗管理・表示切替（リスト/カンバン/タイムライン）を行えます。

## 機能

- **プロジェクト管理**: 複数プロジェクトの作成・編集・削除、色ラベル設定
- **タスク管理**: タスク名、期限、優先度、ステータス、担当者、進捗率の管理
- **表示モード**: 
  - カンバンボード（ドラッグ＆ドロップ対応）
  - リストビュー（ソート・フィルタ対応）
  - タイムラインビュー（ガントチャート形式）
- **検索・フィルタ**: キーワード検索、ステータス・担当者・期限でフィルタ
- **自動バックアップ**: アプリ終了時にJSONエクスポート

## 必要条件

- Python 3.11 以上
- PyQt6

## インストール

```bash
# 依存パッケージのインストール
pip install -r requirements.txt
```

## 実行方法

```bash
python main.py
```

## EXE化（Windows）

```bash
# PyInstallerでEXE化
pip install pyinstaller
pyinstaller task_manager.spec
```

生成されたEXEファイルは `dist/TaskManager.exe` に作成されます。

## プロジェクト構成

```
├── main.py              # エントリーポイント
├── task_manager.py      # タスク管理CRUD操作
├── storage.py           # SQLiteデータベース管理
├── ui/                  # GUIコンポーネント
│   ├── main_window.py   # メインウィンドウ
│   ├── sidebar.py       # サイドバー
│   ├── kanban_board.py  # カンバンボード
│   ├── list_view.py     # リストビュー
│   ├── timeline_view.py # タイムラインビュー
│   ├── task_card.py     # タスクカード
│   └── dialogs.py       # ダイアログ
├── tests/               # テスト
├── logs/                # ログファイル
└── requirements.txt     # 依存パッケージ
```

## データモデル

```json
{
  "id": 1,
  "project_id": 101,
  "name": "資料作成",
  "due_date": "2025-12-10",
  "priority": "高",
  "status": "進行中",
  "progress": 50,
  "assignee": "user1"
}
```

## テスト

```bash
python -m unittest discover -v tests/
```

## ライセンス

MIT License
