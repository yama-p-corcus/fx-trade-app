# FX Trade Journal MVP

PyQt6 と SQLite を使った、FX トレード記録アプリの MVP です。

## 実装済み（MVP）

- 月表示カレンダー
- トレードのある日を損益に応じて色分け
- 日別トレード一覧
- トレードの新規追加 / 編集 / 削除
- SQLite 永続化

## 未実装（今後のステップ）

- 相場分析画像の保存
- ダッシュボード（BI 表示）

## フォルダ構成

```text
.
|-- main.py
|-- requirements.txt
|-- README.md
|-- data/
|   `-- images/
`-- src/
    |-- __init__.py
    |-- controllers/
    |   |-- __init__.py
    |   `-- trade_controller.py
    |-- database/
    |   |-- __init__.py
    |   `-- connection.py
    |-- models/
    |   |-- __init__.py
    |   `-- trade.py
    |-- repositories/
    |   |-- __init__.py
    |   `-- trade_repository.py
    |-- services/
    |   |-- __init__.py
    |   `-- trade_service.py
    `-- ui/
        |-- __init__.py
        |-- dashboard_page.py
        |-- main_window.py
        |-- menu_page.py
        |-- styles.py
        |-- trade_form_dialog.py
        |-- trade_list_page.py
        `-- trade_calendar_page.py
```

## 実行手順

1. 仮想環境を作成

```powershell
python -m venv .venv
```

2. 仮想環境を有効化

```powershell
.venv\Scripts\Activate.ps1
```

3. 依存関係をインストール

```powershell
pip install -r requirements.txt
```

4. アプリを起動

```powershell
python main.py
```

## 補足

- DB ファイルは `data/trades.db` に作成されます。
- 画像保存用の `data/images/` も先に作成されますが、MVP ではまだ使用しません。
- 数値表示は一覧画面で 3 桁区切り表示にしています。
