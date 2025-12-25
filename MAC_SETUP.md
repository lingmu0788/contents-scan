# Mac での セットアップと実行ガイド

Contents Engine 自動化スクリプトを Mac で実行するための手順をご説明します。

## 前提条件

- macOS 10.15 以上
- Python 3.8 以上
- Git
- Chrome ブラウザ（インストール済み）

## セットアップ手順

### 1. リポジトリをクローン

```bash
git clone https://github.com/lingmu0788/contents-scan.git
cd contents-scan/src
```

### 2. 仮想環境を作成

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. 依存パッケージをインストール

```bash
pip install -r requirements.txt
```

### 4. .env ファイルを設定

```bash
# .env.example から .env を作成
cp .env.example .env

# テキストエディタで .env を編集
nano .env
```

`.env` ファイルに以下を入力：

```
EMAIL=your-email@example.com
PASSWORD=your-password
START_SECTION=1
END_SECTION=5
```

**注意:** 実際のメールアドレスとパスワードに置き換えてください。

### 5. 実行

```bash
python3 main.py
```

## 実行モード別の手順

### モード 1: 通常実行（全セクション再生）

```bash
python3 main.py
```

### モード 2: 特定セクション範囲の再生

`.env` ファイルを編集：

```
START_SECTION=2
END_SECTION=5
```

その後実行：

```bash
python3 main.py
```

### モード 3: テスト実行（10秒のみ再生）

```bash
python3 main-2.py
```

### モード 4: セクション/コンテンツ一覧取得

```bash
python3 main-list.py
```

## 実行中の操作

### スクリプトを中断

ターミナルで `Ctrl+C` を押してください。

進捗は自動的に保存されるため、次回実行時は途中から再開できます。

### 進捗をクリア（最初から実行）

```bash
rm progress.json
python3 main.py
```

## トラブルシューティング

### エラー: "command not found: python3"

Python 3 がインストールされていません。以下でインストール：

```bash
# Homebrew を使用
brew install python3
```

### エラー: Chrome not found

Chrome ブラウザをインストールしてください。
https://www.google.com/chrome/

### エラー: "Permission denied"

ファイルの実行権限を付与：

```bash
chmod +x main.py
```

### エラー: Selenium connection error

Chromedriver が正しくダウンロードされるまで待機してください（初回のみ時間がかかります）。

## よくある質問

**Q: 複数のセクションを再生する場合、どのくらい時間がかかりますか？**

A: 各ビデオの長さによって異なります。ビデオが終了するまで自動で再生が続きます。

**Q: セクション番号はどう確認しますか？**

A: 実行画面に「セクション 1/46」のように表示されます。

**Q: 途中で中断したい場合はどうしますか？**

A: `Ctrl+C` を押してください。進捗が自動保存されているため、次回実行時に途中から再開できます。

## サポート

問題が発生した場合は、以下の情報を提供していただくと解決しやすくなります：

- macOS バージョン
- Python バージョン：`python3 --version`
- エラーメッセージ全文
- ターミナル出力ログ

## ライセンス

このプロジェクトはプライベートリポジトリです。

---

**最後に更新**: 2025-12-25

