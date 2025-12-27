# Windows 11 でのセットアップと実行ガイド

Contents Engine 自動化スクリプトを Windows 11 で実行するための詳細な手順をご説明します。

## 前提条件

- Windows 11 OS
- Python 3.8 以上（推奨：Python 3.13）
- Git for Windows
- Chrome ブラウザ（インストール済み）
- PowerShell 5.0 以上（Windows 11 搭載）

## セットアップ手順

### ステップ 1: 必須ソフトウェアのインストール

#### 1-1. Python のインストール

**方法1: 公式サイトからインストール（推奨）**

1. [Python 公式サイト](https://www.python.org/downloads/) にアクセス
2. Windows インストーラー（64-bit）をダウンロード
3. インストーラーを実行
   - ⚠️ **重要：** 「Add Python to PATH」にチェックを入れる ✅
4. 「Install Now」をクリック

**インストール確認：**

PowerShell を開いて以下を実行：

```powershell
python --version
```

出力例：`Python 3.13.0`

#### 1-2. Git for Windows のインストール

1. [Git for Windows](https://git-scm.com/download/win) からダウンロード
2. インストーラーを実行
3. デフォルト設定でインストール

**インストール確認：**

```powershell
git --version
```

出力例：`git version 2.43.0.windows.1`

#### 1-3. Chrome ブラウザの確認

1. Chrome がインストール済みか確認
   - スタートメニューから検索して起動できればOK
2. 未インストールの場合: [Google Chrome](https://www.google.com/chrome/) からダウンロードしてインストール

---

### ステップ 2: プロジェクトをクローン

PowerShell を開いて実行：

```powershell
cd C:\Users\YourUsername
git clone https://github.com/lingmu0788/contents-scan.git
cd contents-scan
```

**ディレクトリ構造の確認：**

```
C:\Users\YourUsername\contents-scan\
├── src\
│   ├── main.py
│   ├── main_test.py
│   ├── .env.example
│   ├── requirements.txt
│   ├── venv\  (まだ作成されていない)
│   └── ...
├── run.sh
├── MAC_SETUP.md
└── WINDOWS_SETUP.md (このファイル)
```

---

### ステップ 3: 仮想環境を作成

#### Windows 用 PowerShell コマンド：

`src` ディレクトリに移動：

```powershell
cd contents-scan\src
```

仮想環境を作成：

```powershell
python -m venv venv
```

⏳ 初回は数秒～数十秒かかります（ネット速度に依存）

**作成確認：**

```powershell
dir venv
```

以下のサブディレクトリが表示されればOK：
- `Scripts`
- `Lib`
- `pyvenv.cfg`

---

### ステップ 4: 仮想環境を有効化

PowerShell で実行（`src` ディレクトリ内から）：

```powershell
.\venv\Scripts\Activate.ps1
```

✅ **成功の目安：** ターミナルのプロンプトが `(venv)` で始まる

例：
```powershell
(venv) PS C:\Users\YourUsername\contents-scan\src>
```

#### ⚠️ エラーが出た場合：

**「Activate.ps1 スクリプトが実行できない」エラー**

以下を実行して、PowerShell の実行ポリシーを変更：

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

「Y」を入力して確認。その後、再度 Activate.ps1 を実行してください。

---

### ステップ 5: 依存パッケージをインストール

**仮想環境が有効な状態で実行：**

```powershell
pip install -r requirements.txt
```

⏳ インストール時間：**1～3 分**（ネット速度に依存）

**インストール確認：**

最後に以下のような出力が出ればOK：
```
Successfully installed selenium-4.15.2 webdriver-manager-4.0.1 python-dotenv-1.0.0
```

---

### ステップ 6: .env ファイルを作成

#### 6-1. .env ファイルを作成

PowerShell で実行（仮想環境が有効な状態）：

```powershell
Copy-Item .env.example .env
```

#### 6-2. .env ファイルを編集

`.env` ファイルをテキストエディタで開いて編集：

**テキストエディタで開く方法：**

- **メモ帳：** `notepad .env`
- **VS Code：** `code .env`
- **手動：** エクスプローラーで `.env` を右クリック → 「プログラムから開く」

**編集内容：**

```.env
EMAIL=your_actual_email@gmail.com
PASSWORD=your_actual_password
```

⚠️ **重要：実際のメールアドレスとパスワードに置き換えてください！**

編集後、ファイルを保存して閉じます。

#### ✅ 確認：

```powershell
cat .env
```

以下のように表示されればOK：
```
EMAIL=your_actual_email@gmail.com
PASSWORD=your_actual_password
```

---

## 実行方法

### 準備完了の確認

以下の状態を確認してください：

- [ ] PowerShell で `src` ディレクトリにいる
- [ ] プロンプトが `(venv)` で始まっている
- [ ] `.env` ファイルが作成されている
- [ ] `.env` に正しいメールアドレスとパスワードが記入されている

---

### 🧪 テスト版を実行（最初のステップ・推奨）

**本番実行の前に、必ずテスト版で動作確認してください！**

```powershell
python main_test.py
```

**テスト版の仕様：**
- ✅ 最初の 1 セクションのみ実行
- ✅ 各ビデオを 30 秒間だけ再生してスキップ
- ✅ 最大 2 コンテンツまでテスト
- ✅ 詳細なログ出力
- ✅ 終了時に Enter キーで確認（ブラウザを見る時間がある）

**テスト実行中の確認項目：**

1. ✅ Chrome ブラウザが自動で起動した？
2. ✅ ログインページが表示された？
3. ✅ メールアドレスとパスワードが自動入力された？
4. ✅ ログイン成功の画面が表示された？
5. ✅ セクション 1 が表示された？
6. ✅ 再生ボタンがクリックされた？
7. ✅ ビデオが再生された？
8. ✅ 30 秒後に自動スキップされた？
9. ✅ 「次へ」ボタンが自動でクリックされた？
10. ✅ メインページに戻った？

**すべて ✅ なら、本番実行に進んでください！**

**テスト版のエラー例と対応：**

| エラー | 原因と対応 |
|--------|----------|
| `No module named 'selenium'` | パッケージがインストールされていない。`pip install -r requirements.txt` を再実行 |
| `Chrome not found` | Chrome がインストールされていない。[Google Chrome](https://www.google.com/chrome/) からインストール |
| `.env ファイルが見つからない` | `.env` ファイルを作成し、メールアドレスとパスワードを入力 |
| ログイン失敗 | `.env` のメールアドレスとパスワードが正しいか確認。スペースないか注意 |

---

### 🚀 本番実行

テスト版が成功したら、本番実行：

```powershell
python main.py
```

**本番実行の仕様：**
- ✅ すべてのセクションを順番に実行
- ✅ 各ビデオを最後まで完全に再生
- ✅ 進捗が自動で保存される
- ✅ 途中で止めても、次回は続きから再開できる

**実行時間の目安：**
- セクション数（約 46 個）× ビデオの平均時間 = 総実行時間
- 例：各セクション平均 15 分 × 46 セクション = 約 11 時間

---

### 実行中の操作

#### 一時停止

ターミナルで `Ctrl+C` を押す：

```
実行中...
^C  ← Ctrl+C を押す
Interrupted! 進捗を保存しました...
```

#### 再開

再度実行：

```powershell
python main.py
```

途中から再開するか聞かれます：
```
前回中断した位置から再開しますか？ (y/n):
```

`y` を入力して Enter。

---

## 実行後の確認

### ログファイル

`src` ディレクトリに `automation_YYYYMMDD_HHMMSS.log` が自動作成されます。

**ログファイルを確認：**

```powershell
dir *.log
```

**ログファイルを開く：**

```powershell
notepad (Get-ChildItem automation_*.log | Sort-Object LastWriteTime -Descending | Select-Object -First 1).Name
```

### 進捗ファイル

`progress.json` に完了したセクション情報が保存されます。

**進捗を確認：**

```powershell
cat progress.json
```

出力例：
```json
{
  "completed_sections": [1, 2, 3],
  "last_section": 3
}
```

---

## よくある操作

### 進捗をリセットする（最初から実行したい）

```powershell
Remove-Item progress.json
python main.py
```

### 特定のセクションだけテストしたい

`main_test.py` をテキストエディタで開いて、以下の部分を編集：

```python
TEST_VIDEO_DURATION = 30  # ビデオ再生時間（秒）
MAX_TEST_CONTENTS = 2      # テストコンテンツ数
TEST_SECTION_INDEX = 1     # テストするセクション（1から始まる）
```

編集後、保存して実行：

```powershell
python main_test.py
```

### ブラウザを表示させたまま実行したい

`main.py` をテキストエディタで開いて、以下の行をコメントアウト（先頭に `#` を付ける）：

```python
# options.add_argument('--headless')  # ← この行の先頭に # を付ける
```

保存して実行：

```powershell
python main.py
```

---

## トラブルシューティング

### 「command not found: python」エラー

**原因：** Python が PATH に登録されていない

**対応：**

1. Python を再インストール
2. インストール時に「Add Python to PATH」にチェック ✅
3. インストール完了後、PowerShell を再起動
4. `python --version` で確認

### 「Activate.ps1 スクリプトが実行できない」エラー

**対応：** 前述の「ステップ 4」で説明した実行ポリシー変更を実行

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 「Module not found: selenium」エラー

**原因：** 仮想環境が有効化されていない

**対応：**

```powershell
# 仮想環境を有効化（src ディレクトリ内から）
.\venv\Scripts\Activate.ps1
```

プロンプトが `(venv)` で始まることを確認。

### ログイン失敗

**確認項目：**

1. `.env` ファイルが存在するか確認：
   ```powershell
   cat .env
   ```

2. メールアドレスとパスワードに**スペースがないか**確認
   - ❌ 例（ダメ）：`EMAIL = user@example.com`
   - ✅ 例（良い）：`EMAIL=user@example.com`

3. 実際のメールアドレスとパスワードが入力されているか確認

4. ブラウザのキャッシュをクリア（必要な場合）

### ブラウザが表示されない

**原因：** ヘッドレスモード（バックグラウンド実行）が有効になっている

**対応：** `main.py` の以下の行をコメントアウト

```python
# options.add_argument('--headless')
```

### 「Chrome not found」エラー

**対応：**

1. Chrome がインストールされているか確認
   - スタートメニューから「Chrome」を検索
2. 未インストール → [Google Chrome](https://www.google.com/chrome/) からインストール
3. インストール完了後、PowerShell を再起動
4. 再度実行

### 再生が途中で止まる

**確認項目：**

1. インターネット接続の確認
2. ログファイルを確認：
   ```powershell
   cat (Get-ChildItem automation_*.log | Sort-Object LastWriteTime -Descending | Select-Object -First 1).Name
   ```
3. スクリプトは自動でリトライします（数回）
4. 完全に失敗した場合は、`Ctrl+C` で中断して再実行

---

## セキュリティ上の注意

⚠️ **.env ファイルには認証情報が含まれます**

- ✅ `.env` ファイルを Git にコミットしない
- ✅ `.gitignore` で保護されています
- ✅ ローカルマシンのみで保管
- ✅ 他の人と共有しない
- ✅ 他の PC でも同じ手順で `.env` を作成（コピーしない）

---

## アップデート（将来の使用）

スクリプトが更新された場合：

```powershell
cd contents-scan
git pull origin main
cd src
# 仮想環境は再利用できます
pip install -r requirements.txt  # 依存パッケージ更新（念のため）
python main_test.py  # テスト実行
python main.py      # 本番実行
```

---

## その他のファイル

### run.sh について

- **用途：** macOS/Linux 用の自動実行スクリプト
- **Windows での使用：** PowerShell では実行できません
- **Windows の代わり：** PowerShell で各コマンドを手動実行

---

## サポート

問題が発生した場合は、以下の情報を確認してください：

- Windows 11 バージョン：`winver` で確認
- Python バージョン：`python --version`
- エラーメッセージ全文
- ログファイル内容（`automation_*.log`）

---

**最終更新：2025-12-27**

**対応環境：** Windows 11 + Python 3.8 以上 + Chrome


