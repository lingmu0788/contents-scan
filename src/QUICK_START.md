# 🚀 クイックスタートガイド

Contents Engine マスタープログラム自動化ツールの使い方

## 📋 セットアップ（初回のみ）

### macOS/Linux ユーザー向け簡単実行方法（推奨）

**プロジェクトルート** = `/Users/suzukishinji/projects/contents-scan/` で以下のコマンドを実行するだけ：

```bash
cd /Users/suzukishinji/projects/contents-scan
./run.sh
```

このスクリプトが自動的に以下を実行します：
- ✅ src ディレクトリに移動
- ✅ 仮想環境を有効化
- ✅ main.py を実行

**ディレクトリ構造：**
```
/Users/suzukishinji/projects/contents-scan/  ← プロジェクトルート
├── run.sh  ← ここから実行
├── src/
│   ├── main.py
│   └── venv/
└── その他
```

---

### ステップ1：.envファイルを作成

**Windows の場合：**
```powershell
cd C:\Users\SS9212\projects\contents-scan\src
Copy-Item .env.example .env
```

**macOS/Linux の場合：**
```bash
cd /Users/suzukishinji/projects/contents-scan/src
cp .env.example .env
```

### ステップ2：.envファイルを編集

メモ帳やVSCodeで `.env` ファイルを開いて、以下を入力：

```
EMAIL=your_actual_email@gmail.com
PASSWORD=your_actual_password
```

**⚠️ 注意：本物のメールアドレスとパスワードに置き換えてください！**

### ステップ3：仮想環境を有効化

**Windows の場合：**
```powershell
cd C:\Users\SS9212\projects\contents-scan\src
.\venv\Scripts\Activate.ps1
```

**macOS/Linux の場合：**
```bash
cd /Users/suzukishinji/projects/contents-scan/src
source venv/bin/activate
```

プロンプトが `(venv)` で始まることを確認してください。

#### 👍 推奨：run.sh を使う方法（macOS/Linux）

プロジェクトルート（`/Users/suzukishinji/projects/contents-scan/`）で実行：

```bash
./run.sh
```

このスクリプトが自動的に以下を実行します：
- ✅ src ディレクトリに移動
- ✅ 仮想環境を有効化
- ✅ main.py を実行

---

## 🧪 テスト実行（必須！）

**まずはテスト版で動作確認しましょう！**

**Windows の場合：**
```powershell
python main_test.py
```

**macOS/Linux の場合：**
```bash
./run.sh  # またはソースコードから cd src && source venv/bin/activate && python main_test.py
```

### テスト版で何が起こるか？

1. ブラウザが自動で開く
2. ログインが自動で実行される
3. 最初のセクションの最初の2コンテンツだけ再生される
4. 各ビデオは30秒間だけ再生してスキップ
5. 終了後、Enterキーを押すまでブラウザが開いたまま（確認できる）

### テスト結果の確認

- ✅ ログインできた？
- ✅ 再生ボタンが自動でクリックされた？
- ✅ ビデオが再生された？
- ✅ 「次へ」ボタンがクリックされた？
- ✅ メインページに戻れた？

**すべて ✅ なら、本番実行できます！**

---

## 🎯 本番実行

テストが成功したら、本番実行：

**Windows の場合：**
```powershell
python main.py
```

**macOS/Linux の場合：**
```bash
./run.sh
```

### 本番実行で何が起こるか？

1. すべてのセクションを順番に実行
2. 各ビデオを最後まで完全に再生
3. 進捗が自動で保存される
4. 途中で止めても、次回は続きから再開できる

### 実行中の操作

- **一時停止**: `Ctrl+C` を押す
- **再開**: 再度 `python main.py` を実行

---

## 📊 実行後の確認

### ログファイル

`automation_YYYYMMDD_HHMMSS.log` に詳細ログが保存されます。

エラーが発生した場合はこのファイルを確認してください。

### 進捗ファイル

`progress.json` に完了したセクションが保存されます。

```json
{
  "completed_sections": [1, 2, 3],
  "last_section": 3
}
```

---

## ❓ よくある質問

### Q: テストだけ実行したい

A: `python main_test.py` を実行してください。

### Q: 特定のセクションだけテストしたい

A: `main_test.py` の15行目を編集：

```python
TEST_SECTION_INDEX = 3  # 3番目のセクションをテスト
```

### Q: もっと長くテストしたい

A: `main_test.py` の13-14行目を編集：

```python
TEST_VIDEO_DURATION = 60  # 60秒間再生
MAX_TEST_CONTENTS = 5     # 5コンテンツまでテスト
```

### Q: 進捗をリセットしたい

A: `progress.json` を削除：

```powershell
Remove-Item progress.json
```

### Q: エラーが出た

A: 以下を確認：
1. `.env` ファイルにメールアドレスとパスワードが正しく設定されているか
2. インターネット接続があるか
3. ログファイル（`automation_*.log` または `test_*.log`）を確認

---

## 💡 ヒント

- テスト版は何度実行しても進捗に影響しません
- 本番実行は長時間かかるので、時間に余裕があるときに実行してください
- Ctrl+C で安全に中断できます（進捗は保存されます）
- ログファイルは毎回新しいファイルが作成されます

---

## 🆘 サポート

問題が発生した場合は、ログファイルを確認してください：

```powershell
# 最新のログファイルを開く（テスト版）
notepad (Get-ChildItem test_*.log | Sort-Object LastWriteTime -Descending | Select-Object -First 1).Name

# 最新のログファイルを開く（本番）
notepad (Get-ChildItem automation_*.log | Sort-Object LastWriteTime -Descending | Select-Object -First 1).Name
```

---

**準備ができたら、テスト実行してみましょう！** 🚀

```powershell
python main_test.py
```

