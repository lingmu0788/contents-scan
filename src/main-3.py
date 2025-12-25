"""
Contents Engine マスタープログラム（Hitomi）自動化スクリプト - 選択可能版

このスクリプトは、会員サイトのセクションを自動で上から順番に再生します。
【選択可能版の特徴】
- 起動時に再生モードを選択可能
  1. テストモード：各動画を10秒だけ再生（高速検証用）
  2. 本番モード：各動画を最後まで完全再生
- ビデオ終了を自動検出
- 進捗保存機能
- ログ出力機能
- エラーリトライ機能
"""

import os
import sys
import time
import json
import logging
from datetime import datetime
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Windowsコンソールでの文字化けを回避
if sys.platform == 'win32':
    try:
        # PowerShellのコードページをUTF-8に設定を試みる
        import subprocess
        subprocess.run(['chcp', '65001'], shell=True, capture_output=True)
    except:
        pass
    
    # 元のprint関数を保持
    import builtins
    _original_print = builtins.print
    
    def safe_print(*args, **kwargs):
        """文字化けを回避した安全なprint関数"""
        try:
            _original_print(*args, **kwargs)
        except UnicodeEncodeError:
            # エンコーディングエラーが発生した場合、絵文字を除去して再試行
            try:
                text = ' '.join(str(arg) for arg in args)
                # 絵文字を除去（簡易版）
                import re
                text = re.sub(r'[^\x00-\x7F]+', '', text)  # ASCII以外を除去
                _original_print(text, **kwargs)
            except:
                # それでもエラーなら、エンコーディングエラーを無視
                pass
    
    # print関数を安全なバージョンで置き換え
    builtins.print = safe_print

# .env ファイルから環境変数を読み込む
load_dotenv()

# 設定値
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
URL = 'https://letter.the-3rd-brain.com/members/C3sxfGdWUas4/course/UZr4qDbqxh9I'
PROGRESS_FILE = 'progress.json'
LOG_FILE = f'automation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

# セクション範囲設定（.env または環境変数から読み込み）
# 例: START_SECTION=3, END_SECTION=4 でセクション3-4のみ再生
START_SECTION = os.getenv('START_SECTION')
END_SECTION = os.getenv('END_SECTION')

# グローバル変数：再生モード（起動時にユーザーが選択、または .env から読み込み）
PLAYBACK_MODE = os.getenv('PLAYBACK_MODE', 'full').lower()  # 'test' または 'full'
if PLAYBACK_MODE not in ['test', 'full']:
    PLAYBACK_MODE = 'full'

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def load_progress():
    """進捗状況を読み込む"""
    try:
        if os.path.exists(PROGRESS_FILE):
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logging.warning(f"進捗ファイル読み込みエラー: {e}")
    return {'completed_sections': [], 'last_section': 0}

def save_progress(section_index):
    """進捗状況を保存"""
    try:
        progress = load_progress()
        if section_index not in progress['completed_sections']:
            progress['completed_sections'].append(section_index)
        progress['last_section'] = section_index
        with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
        logging.info(f"✅ 進捗を保存しました: セクション {section_index}")
    except Exception as e:
        logging.error(f"進捗保存エラー: {e}")

def setup_driver():
    """Chromeドライバーをセットアップ"""
    # 既存のChromeDriverとChromeプロセスをクリーンアップ
    try:
        import subprocess
        if sys.platform == 'win32':
            # Windowsの場合、既存のchromedriverとchromeプロセスを終了
            subprocess.run(['taskkill', '/F', '/IM', 'chromedriver.exe'], 
                         capture_output=True, stderr=subprocess.DEVNULL)
            subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], 
                         capture_output=True, stderr=subprocess.DEVNULL)
            time.sleep(1)  # プロセス終了を待つ
    except:
        pass
    
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # ヘッドレスモード（画面を表示しない場合は有効にする）
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')  # 自動化検出を回避
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()  # ウィンドウを最大化
    return driver

def login(driver, email, password):
    """ログイン処理"""
    logging.info("🔐 ログインしています...")
    
    # ログインページにアクセス
    driver.get(URL)
    
    # ログイン画面が表示されるまで待機
    wait = WebDriverWait(driver, 10)
    
    try:
        # メールアドレス入力フィールドを取得
        email_input = wait.until(
            EC.presence_of_element_located((By.NAME, 'email'))
        )
        email_input.send_keys(email)
        logging.info("✅ メールアドレスを入力しました")
        
        # パスワード入力フィールドを取得
        password_input = driver.find_element(By.NAME, 'password')
        password_input.send_keys(password)
        logging.info("✅ パスワードを入力しました")
        
        # ログインボタンをクリック
        login_button = driver.find_element(By.XPATH, '//button[contains(text(), "ログイン")]')
        login_button.click()
        logging.info("✅ ログインボタンをクリックしました")
        
        # ログイン完了を待機（セクション一覧が表示されるまで）
        wait.until(
            EC.presence_of_all_elements_located((By.XPATH, '//button[contains(text(), "受講する")]'))
        )
        logging.info("✅ ログイン完了！セクション一覧が表示されました\n")
        
        return True
    except Exception as e:
        logging.error(f"❌ ログイン処理でエラーが発生しました: {e}")
        return False

def get_all_sections(driver):
    """ページ内のすべての「受講する」ボタンを取得"""
    try:
        buttons = driver.find_elements(By.XPATH, '//button[contains(text(), "受講する")]')
        logging.info(f"📊 合計 {len(buttons)} 個のセクションが見つかりました\n")
        return buttons
    except Exception as e:
        logging.error(f"❌ セクション取得エラー: {e}")
        return []

def play_content(driver, section_index=None, content_index=None, retry_count=3, playback_mode='full'):
    """単一のコンテンツを再生（ビデオ終了まで）"""
    for attempt in range(retry_count):
        try:
            wait = WebDriverWait(driver, 15)
            
            # セクション番号とコンテンツ番号を表示
            if section_index and content_index:
                print(f"\r[セクション {section_index} / コンテンツ {content_index}] 再生中...", end='', flush=True)
            
            # 1. 再生ボタンを検索してクリック
            logging.info("  🎬 再生ボタンを探してクリック...")
            play_button_clicked = False
            
            # 複数の再生ボタンパターンを試行
            play_button_selectors = [
                '//button[contains(@aria-label, "play") or contains(@aria-label, "再生")]',
                '//button[@class and contains(@class, "play")]',
                '//div[contains(@class, "video")]//button',
                '//div[contains(@class, "player")]//button',
                '//button[contains(@class, "vjs-big-play-button")]',  # Video.js
                '//div[@class and contains(@class, "play")]',
            ]
            
            for selector in play_button_selectors:
                try:
                    play_button = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    play_button.click()
                    logging.info("  ✅ 再生ボタンをクリックしました")
                    play_button_clicked = True
                    time.sleep(3)  # ビデオ読み込み待機
                    break
                except:
                    continue
            
            if not play_button_clicked:
                logging.warning("  ⚠️ 再生ボタンが見つかりません（自動再生の可能性）")
            
            # 2. ビデオ再生完了まで待機
            logging.info("  ⏳ ビデオ再生中（終了まで待機）...")
            
            # iframe があるか確認して切り替え
            try:
                iframes = driver.find_elements(By.TAG_NAME, 'iframe')
                if iframes:
                    logging.info(f"  🔍 iframe を発見しました（{len(iframes)}個）、切り替えます...")
                    driver.switch_to.frame(iframes[0])
                    logging.info("  ✅ iframe に切り替えました")
                    time.sleep(2)
            except Exception as iframe_e:
                logging.warning(f"  ⚠️ iframe切り替えエラー: {iframe_e}")
            
            try:
                # ビデオ要素を探す（iframe内）
                video = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'video'))
                )
                logging.info("  ✅ ビデオ要素が見つかりました")
                
                # JavaScriptで直接ビデオを再生
                try:
                    driver.execute_script("arguments[0].play();", video)
                    logging.info("  ✅ JavaScriptでビデオ再生を開始しました")
                    time.sleep(3)  # 再生開始を待つ
                except Exception as play_e:
                    logging.warning(f"  ⚠️ JavaScript再生エラー: {play_e}")
                
                # ビデオが再生開始するまで待機
                time.sleep(2)
                
                # 再生モードに応じて待機時間を設定
                if playback_mode == 'test':
                    max_wait = 10  # テストモード：10秒だけ再生
                    logging.info(f"  ⏳ テストモード：{max_wait}秒だけ再生します")
                else:
                    max_wait = 3600  # 本番モード：最大1時間（通常は動画終了で自動停止）
                    logging.info(f"  ⏳ 本番モード：動画が終了するまで再生します")
                
                elapsed = 0
                last_time = 0
                stall_count = 0
                
                while elapsed < max_wait:
                    try:
                        current_time = video.get_property('currentTime')
                        duration = video.get_property('duration')
                        paused = video.get_property('paused')
                        
                        if duration and current_time is not None:
                            # 10秒ごとに進捗表示
                            if int(elapsed) % 10 == 0 and elapsed > 0:
                                progress = (current_time / duration * 100) if duration > 0 else 0
                                section_info = f"[セクション {section_index}]" if section_index else ""
                                content_info = f"[コンテンツ {content_index}]" if content_index else ""
                                status_msg = f"  ⏱️  {section_info} {content_info} 再生中: {int(current_time)}/{int(duration)}秒 ({progress:.1f}%)"
                                logging.info(status_msg)
                                # プロンプトにも表示
                                if section_index and content_index:
                                    print(f"\r[セクション {section_index} / コンテンツ {content_index}] {int(current_time)}/{int(duration)}秒 ({progress:.1f}%)", end='', flush=True)
                            
                            # 停止検出（同じ時間が5秒以上続く場合）
                            if abs(current_time - last_time) < 0.5:
                                stall_count += 1
                                if stall_count > 5 and paused:
                                    logging.warning("  ⚠️ ビデオが一時停止しています。再生を試みます...")
                                    try:
                                        driver.execute_script("arguments[0].play();", video)
                                        stall_count = 0
                                    except:
                                        pass
                            else:
                                stall_count = 0
                            
                            last_time = current_time
                            
                            # ビデオが終了したかチェック
                            if current_time >= duration - 1:  # 1秒の余裕を持たせる
                                logging.info(f"  ✅ ビデオ再生完了: {int(duration)}秒")
                                if section_index and content_index:
                                    print(f"\n[セクション {section_index} / コンテンツ {content_index}] ビデオ再生完了！")
                                break
                    except Exception as e:
                        logging.debug(f"  ビデオ状態チェック中: {e}")
                    
                    time.sleep(1)
                    elapsed += 1
                
                if elapsed >= max_wait:
                    if playback_mode == 'test':
                        logging.warning(f"  ⚠️ テストモード：{max_wait}秒経過したので次に進みます")
                    else:
                        logging.warning(f"  ⚠️ 最大待機時間に達しました")
                    
            except Exception as e:
                logging.warning(f"  ⚠️ ビデオ要素が見つかりません: {e}")
            
            # iframe から戻る
            try:
                driver.switch_to.default_content()
                logging.info("  🔙 iframe からメインコンテンツに戻りました")
            except:
                pass
            
            # 3. 「次へ」ボタンをクリック
            logging.info("  📌 「次へ」ボタンをクリック...")
            
            # まず、ページ内のすべてのボタンとリンクを確認して「次へ」を含むものを探す
            next_button_text = None
            next_button_found = False
            
            try:
                all_buttons = driver.find_elements(By.TAG_NAME, 'button')
                for btn in all_buttons:
                    try:
                        btn_text = btn.text.strip()
                        if btn_text and ('次へ' in btn_text or 'next' in btn_text.lower()):
                            logging.info(f"  ✅ 「次へ」ボタンを発見: '{btn_text}'")
                            next_button_text = btn_text
                            next_button_found = True
                            break
                    except:
                        continue
                
                if not next_button_found:
                    all_links = driver.find_elements(By.TAG_NAME, 'a')
                    for link in all_links:
                        try:
                            link_text = link.text.strip()
                            if link_text and ('次へ' in link_text or 'next' in link_text.lower()):
                                logging.info(f"  ✅ 「次へ」リンクを発見: '{link_text}'")
                                next_button_text = link_text
                                next_button_found = True
                                break
                        except:
                            continue
            except Exception as find_e:
                logging.debug(f"  ボタン検索エラー: {find_e}")
            
            # 見つかったテキストを使ってセレクタを作成
            if next_button_text:
                next_button_selectors = [
                    f'//button[contains(text(), "{next_button_text}")]',
                    f'//a[contains(text(), "{next_button_text}")]',
                    '//button[contains(text(), "次へ")]',
                    '//a[contains(text(), "次へ")]',
                    '//button[contains(@class, "next")]',
                    '//a[contains(@class, "next")]',
                ]
            else:
                # テキストが見つからない場合のフォールバック
                next_button_selectors = [
                    '//button[contains(text(), "次へ")]',
                    '//a[contains(text(), "次へ")]',
                    '//button[contains(@class, "next")]',
                    '//a[contains(@class, "next")]',
                ]
            
            next_button = None
            for selector in next_button_selectors:
                try:
                    next_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    logging.info(f"  ✅ 「次へ」ボタン要素を取得しました")
                    break
                except:
                    continue
            
            if next_button:
                try:
                    next_button.click()
                    logging.info("  ✅ 「次へ」ボタンをクリックしました")
                    time.sleep(3)  # ページ遷移待機
                    return True
                except Exception as click_e:
                    logging.warning(f"  ⚠️ 「次へ」ボタンのクリックエラー: {click_e}")
                    # JavaScriptでクリックを試みる
                    try:
                        driver.execute_script("arguments[0].click();", next_button)
                        logging.info("  ✅ JavaScriptで「次へ」ボタンをクリックしました")
                        time.sleep(3)
                        return True
                    except:
                        pass
            
            logging.info(f"  ℹ️ 「次へ」ボタンが見つかりません（セクション終了）")
            return False
                
        except Exception as e:
            if attempt < retry_count - 1:
                logging.warning(f"  ⚠️ コンテンツ再生エラー（リトライ {attempt + 1}/{retry_count}）: {e}")
                time.sleep(3)
            else:
                logging.error(f"  ❌ コンテンツ再生エラー（最終試行失敗）: {e}")
                return False
    
    return False

def play_section(driver, section_index, total_all_sections, total_active_sections=None, current_position=None, playback_mode='full'):
    """セクションをすべてのコンテンツとともに再生"""
    # デバッグ：受け取ったsection_indexを確認
    logging.info(f"🔍 play_section: section_index={section_index}, total_all_sections={total_all_sections}, total_active={total_active_sections}, position={current_position}, mode={playback_mode}")
    
    # 実際のセクション番号を表示（範囲指定時は範囲内の位置も表示）
    if current_position is not None and total_active_sections is not None:
        display_text = f"セクション {section_index}（範囲内 {current_position}/{total_active_sections}）"
    else:
        display_text = f"セクション {section_index}/{total_all_sections}"
    
    logging.info(f"\n{'='*60}")
    logging.info(f"🎬 {display_text} を再生開始")
    logging.info(f"{'='*60}")
    print(f"\n{'='*60}")
    print(f"🎬 {display_text} を再生開始")
    print(f"{'='*60}")
    
    try:
        wait = WebDriverWait(driver, 15)
        parent_window = driver.current_window_handle
        
        # 「受講する」ボタンをクリック
        buttons = driver.find_elements(By.XPATH, '//button[contains(text(), "受講する")]')
        button_index = section_index - 1  # 0ベースインデックスに変換
        logging.info(f"🔍 デバッグ: セクション{section_index}を再生するため、ボタンインデックス{button_index}（{len(buttons)}個中）をクリックします")
        if button_index < len(buttons):
            # クリックするボタンのテキストを確認（デバッグ用）
            try:
                button_text = buttons[button_index].text
                logging.info(f"🔍 デバッグ: クリックするボタンのテキスト: '{button_text}'")
            except:
                pass
            buttons[button_index].click()
            logging.info(f"✅ セクション{section_index}の「受講する」ボタン（インデックス{button_index}）をクリックしました")
            
            # ページ遷移待機
            time.sleep(3)
            
            # ウィンドウ切り替え（新規ウィンドウが開く場合）
            if len(driver.window_handles) > 1:
                driver.switch_to.window(driver.window_handles[-1])
                logging.info("✅ コンテンツページに切り替えました")
            
            # セクション内のすべてのコンテンツを再生
            content_index = 1
            max_contents = 50  # 無限ループ防止
            
            while content_index <= max_contents:
                logging.info(f"\n  📝 コンテンツ {content_index} を再生...")
                print(f"\n[セクション {section_index} / コンテンツ {content_index}] 再生開始...")
                
                # コンテンツを再生（再生モードを渡す）
                if play_content(driver, section_index=section_index, content_index=content_index, playback_mode=playback_mode):
                    content_index += 1
                    print(f"\n[セクション {section_index} / コンテンツ {content_index - 1}] 完了！")
                else:
                    # 「次へ」ボタンがない場合、セクション終了
                    logging.info(f"\n✅ セクション {section_index} の全コンテンツが完了しました！（合計: {content_index - 1}個）")
                    print(f"\n[セクション {section_index}] 全コンテンツ完了！（合計: {content_index - 1}個）")
                    break
            
            if content_index > max_contents:
                logging.warning(f"⚠️ コンテンツ数が上限に達しました")
            
            # メインページに戻る（戻るボタンをクリック）
            logging.info("  🔙 メインページに戻ります...")
            try:
                # 左上の戻るボタンを探してクリック
                back_button_selectors = [
                    '//button[@aria-label="戻る" or contains(@class, "back")]',
                    '//a[contains(@href, "/course/")]',
                    '//button[contains(text(), "戻る")]',
                    '//a[contains(text(), "Home")]',
                ]
                
                back_button_found = False
                for selector in back_button_selectors:
                    try:
                        back_button = WebDriverWait(driver, 3).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        back_button.click()
                        logging.info("  ✅ 戻るボタンをクリックしました")
                        back_button_found = True
                        time.sleep(2)
                        break
                    except:
                        continue
                
                if not back_button_found:
                    # 戻るボタンが見つからない場合、ブラウザの戻る機能を使用
                    driver.back()
                    logging.info("  ✅ ブラウザの戻る機能を使用しました")
                    time.sleep(2)
                    
            except Exception as e:
                logging.warning(f"  ⚠️ 戻る操作エラー: {e}")
            
            # ウィンドウが複数ある場合は閉じる
            if len(driver.window_handles) > 1:
                try:
                    driver.close()
                    driver.switch_to.window(parent_window)
                except:
                    pass
            
            # メインページに戻ったことを確認
            try:
                wait.until(
                    EC.presence_of_all_elements_located((By.XPATH, '//button[contains(text(), "受講する")]'))
                )
                logging.info("✅ メインページに戻りました\n")
            except:
                logging.warning("⚠️ メインページの確認ができませんでした")
            
            # 進捗を保存
            save_progress(section_index)
            
            print(f"\n[セクション {section_index}] 完了！")
            
            return True
        else:
            logging.error(f"❌ セクション {section_index} のボタンが見つかりません")
            return False
            
    except Exception as e:
        logging.error(f"❌ セクション再生エラー: {e}")
        try:
            if len(driver.window_handles) > 1:
                driver.close()
            driver.switch_to.window(parent_window)
        except:
            pass
        return False

def main():
    """メイン処理"""
    global PLAYBACK_MODE
    
    logging.info("=" * 60)
    logging.info("🚀 Contents Engine マスタープログラム 自動化ツール v3.0")
    logging.info("=" * 60)
    logging.info("")
    
    # 再生モード選択（.env から PLAYBACK_MODE が設定されていない場合のみ対話)
    if PLAYBACK_MODE not in ['test', 'full']:
        PLAYBACK_MODE = 'full'
    
    # 環境変数で指定されていない場合のみ対話的に選択
    playback_mode_env = os.getenv('PLAYBACK_MODE', '').lower()
    if not playback_mode_env:
        print("\n" + "=" * 60)
        print("再生モードを選択してください:")
        print("=" * 60)
        print("1. テストモード（各動画10秒のみ再生）")
        print("2. 本番モード（各動画を最後まで完全再生）")
        print("=" * 60)
        
        while True:
            try:
                mode_choice = input("\n選択してください (1 または 2): ").strip()
                if mode_choice == '1':
                    PLAYBACK_MODE = 'test'
                    print("\n✅ テストモードを選択しました（各動画10秒のみ再生）\n")
                    logging.info("📌 再生モード: テストモード（10秒）")
                    break
                elif mode_choice == '2':
                    PLAYBACK_MODE = 'full'
                    print("\n✅ 本番モードを選択しました（各動画を最後まで再生）\n")
                    logging.info("📌 再生モード: 本番モード（完全再生）")
                    break
                else:
                    print("⚠️ 1 または 2 を入力してください")
            except EOFError:
                # バックグラウンド実行時はデフォルトで本番モード
                PLAYBACK_MODE = 'full'
                print("\n⚠️ 入力なし。デフォルトで本番モードを使用します\n")
                logging.info("📌 再生モード: 本番モード（デフォルト）")
                break
    else:
        # 環境変数から読み込まれた場合
        if PLAYBACK_MODE == 'test':
            print("\n✅ テストモードを使用します（各動画10秒のみ再生）\n")
            logging.info("📌 再生モード: テストモード（10秒）")
        else:
            print("\n✅ 本番モードを使用します（各動画を最後まで再生）\n")
            logging.info("📌 再生モード: 本番モード（完全再生）")
    
    time.sleep(1)
    
    # 環境変数の確認
    if not EMAIL or not PASSWORD:
        logging.error("❌ エラー: .env ファイルにメールアドレスとパスワードが設定されていません")
        logging.info("📝 手順:")
        logging.info("  1. .env.example を .env にコピー")
        logging.info("  2. メールアドレスとパスワードを入力")
        logging.info("  3. このスクリプトを再実行してください")
        return
    
    # 進捗の読み込み
    progress = load_progress()
    completed = progress.get('completed_sections', [])
    
    if completed:
        logging.info(f"📋 前回の進捗が見つかりました")
        logging.info(f"   完了済みセクション: {completed}")
        try:
            response = input("\n前回の続きから再開しますか？ (y/n): ").strip().lower()
            if response != 'y':
                logging.info("最初から開始します...")
                completed = []
                if os.path.exists(PROGRESS_FILE):
                    os.remove(PROGRESS_FILE)
        except EOFError:
            # バックグラウンド実行時は最初から
            logging.info("最初から開始します...")
            completed = []
            if os.path.exists(PROGRESS_FILE):
                os.remove(PROGRESS_FILE)
    
    driver = None
    try:
        # ドライバーセットアップ
        driver = setup_driver()
        logging.info("✅ ブラウザを起動しました\n")
        
        # ログイン
        if not login(driver, EMAIL, PASSWORD):
            logging.error("❌ ログインに失敗しました")
            return
        
        # セクション一覧を取得
        sections = get_all_sections(driver)
        if not sections:
            logging.error("❌ セクションが見つかりません")
            return
        
        # セクション範囲の設定
        start_section = None
        end_section = None
        
        if START_SECTION:
            try:
                start_section = int(START_SECTION)
                logging.info(f"📌 開始セクション: {start_section}")
            except ValueError:
                logging.warning(f"⚠️ START_SECTION の値が無効です: {START_SECTION}")
        
        if END_SECTION:
            try:
                end_section = int(END_SECTION)
                logging.info(f"📌 終了セクション: {end_section}")
            except ValueError:
                logging.warning(f"⚠️ END_SECTION の値が無効です: {END_SECTION}")
        
        # 範囲の検証
        if start_section and (start_section < 1 or start_section > len(sections)):
            logging.error(f"❌ 開始セクション {start_section} が範囲外です（1-{len(sections)}）")
            return
        
        if end_section and (end_section < 1 or end_section > len(sections)):
            logging.error(f"❌ 終了セクション {end_section} が範囲外です（1-{len(sections)}）")
            return
        
        if start_section and end_section and start_section > end_section:
            logging.error(f"❌ 開始セクション {start_section} が終了セクション {end_section} より大きいです")
            return
        
        # 再生範囲を決定
        if start_section and end_section:
            section_range = range(start_section, end_section + 1)
            logging.info(f"📋 セクション {start_section} から {end_section} までを再生します")
            print(f"\n📋 セクション {start_section} から {end_section} までを再生します")
        elif start_section:
            section_range = range(start_section, len(sections) + 1)
            logging.info(f"📋 セクション {start_section} から最後までを再生します")
            print(f"\n📋 セクション {start_section} から最後までを再生します")
        elif end_section:
            section_range = range(1, end_section + 1)
            logging.info(f"📋 セクション 1 から {end_section} までを再生します")
            print(f"\n📋 セクション 1 から {end_section} までを再生します")
        else:
            section_range = range(1, len(sections) + 1)
            logging.info(f"📋 すべてのセクション（1-{len(sections)}）を再生します")
            print(f"\n📋 すべてのセクション（1-{len(sections)}）を再生します")
        
        logging.info("")
        
        # 各セクションを再生
        success_count = 0
        failed_sections = []
        
        # 範囲内のセクションリストを作成（スキップ済みを除く）
        active_sections = [i for i in section_range if i not in completed]
        total_active = len(active_sections)
        current_index = 0
        
        for i in section_range:
            # 完了済みセクションはスキップ
            if i in completed:
                logging.info(f"⏭️  セクション {i} はスキップします（完了済み）")
                print(f"\n⏭️  セクション {i} はスキップします（完了済み）")
                continue
            
            # 現在のセクションが範囲内の何番目かを計算
            current_index += 1
            
            try:
                # 実際のセクション番号（i）を渡す（表示用の位置も渡す、再生モードも渡す）
                if play_section(driver, i, len(sections), total_active, current_index, PLAYBACK_MODE):
                    success_count += 1
                    print(f"\n✅ セクション {i} の再生が正常に完了しました")
                else:
                    failed_sections.append(i)
                    logging.warning(f"⚠️ セクション {i} の再生に問題がありました")
                    print(f"\n⚠️ セクション {i} の再生に問題がありました")
                
                # 指定範囲の最後のセクションが完了した場合、ループを終了
                if end_section and i == end_section:
                    logging.info(f"✅ 指定された範囲（セクション {start_section or 1}-{end_section}）の再生が完了しました")
                    print(f"\n✅ 指定された範囲（セクション {start_section or 1}-{end_section}）の再生が完了しました")
                    break
                
                # 次のセクションへ移動する前に少し待機
                time.sleep(3)
                    
            except Exception as e:
                logging.error(f"❌ セクション {i} でエラー: {e}")
                print(f"\n❌ セクション {i} でエラー: {e}")
                failed_sections.append(i)
                
                # エラーが発生しても、指定範囲の最後のセクションなら終了
                if end_section and i == end_section:
                    break
        
        # 結果サマリー
        print("\n" + "=" * 60)
        print("📊 実行結果サマリー")
        print("=" * 60)
        logging.info("\n" + "=" * 60)
        logging.info("📊 実行結果サマリー")
        logging.info("=" * 60)
        
        # 再生モード表示
        mode_display = "テストモード（10秒）" if PLAYBACK_MODE == 'test' else "本番モード（完全再生）"
        print(f"🎬 再生モード: {mode_display}")
        logging.info(f"🎬 再生モード: {mode_display}")
        
        if start_section and end_section:
            print(f"📋 再生範囲: セクション {start_section}-{end_section}")
            logging.info(f"📋 再生範囲: セクション {start_section}-{end_section}")
        elif start_section:
            print(f"📋 再生範囲: セクション {start_section}-{len(sections)}")
            logging.info(f"📋 再生範囲: セクション {start_section}-{len(sections)}")
        elif end_section:
            print(f"📋 再生範囲: セクション 1-{end_section}")
            logging.info(f"📋 再生範囲: セクション 1-{end_section}")
        else:
            print(f"📋 再生範囲: すべてのセクション（1-{len(sections)}）")
            logging.info(f"📋 再生範囲: すべてのセクション（1-{len(sections)}）")
        print(f"✅ 成功: {success_count} セクション")
        print(f"⏭️  スキップ: {len(completed)} セクション")
        logging.info(f"✅ 成功: {success_count} セクション")
        logging.info(f"⏭️  スキップ: {len(completed)} セクション")
        if failed_sections:
            print(f"⚠️ 失敗: {len(failed_sections)} セクション - {failed_sections}")
            logging.warning(f"⚠️ 失敗: {len(failed_sections)} セクション - {failed_sections}")
        else:
            if start_section and end_section:
                print(f"🎉 指定範囲（セクション {start_section}-{end_section}）の再生が完了しました！")
                logging.info(f"🎉 指定範囲（セクション {start_section}-{end_section}）の再生が完了しました！")
            else:
                print("🎉 すべてのセクションの再生が完了しました！")
                logging.info("🎉 すべてのセクションの再生が完了しました！")
        print(f"📄 ログファイル: {LOG_FILE}")
        print("=" * 60)
        print("\n✅ プログラムを終了します...")
        logging.info(f"📄 ログファイル: {LOG_FILE}")
        logging.info("=" * 60)
        
    except KeyboardInterrupt:
        logging.info("\n⚠️ ユーザーによって中断されました")
        logging.info(f"📋 進捗は保存されています。次回は途中から再開できます。")
    except Exception as e:
        logging.error(f"❌ 予期しないエラーが発生しました: {e}")
        import traceback
        logging.error(traceback.format_exc())
    finally:
        if driver:
            try:
                driver.quit()
                logging.info("\n✅ ブラウザを閉じました")
            except:
                pass

if __name__ == '__main__':
    main()




