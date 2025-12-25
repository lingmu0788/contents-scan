"""
Contents Engine マスタープログラム（Hitomi）自動化スクリプト - クイックテスト版

【テスト版の特徴】
- 各動画を最初の10秒だけ再生（高速検証用）
- .envで指定された範囲のすべてのセクションを対象
- 各セクションのすべてのコンテンツを対象
- 実行前にコンテンツ一覧を表示
- ユーザーが再生開始位置を選択可能
"""

import os
import sys
import time
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
        import subprocess
        subprocess.run(['chcp', '65001'], shell=True, capture_output=True)
    except:
        pass
    
    import builtins
    _original_print = builtins.print
    
    def safe_print(*args, **kwargs):
        """文字化けを回避した安全なprint関数"""
        try:
            _original_print(*args, **kwargs)
        except UnicodeEncodeError:
            try:
                text = ' '.join(str(arg) for arg in args)
                import re
                text = re.sub(r'[^\x00-\x7F]+', '', text)
                _original_print(text, **kwargs)
            except:
                pass
    
    builtins.print = safe_print

# .env ファイルから環境変数を読み込む
load_dotenv()

# 設定値
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
URL = 'https://letter.the-3rd-brain.com/members/C3sxfGdWUas4/course/UZr4qDbqxh9I'
LOG_FILE = f'quick_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

START_SECTION = os.getenv('START_SECTION')
END_SECTION = os.getenv('END_SECTION')

# テスト設定
TEST_VIDEO_DURATION = 10  # 10秒だけ再生

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def setup_driver():
    """Chromeドライバーをセットアップ"""
    try:
        import subprocess
        if sys.platform == 'win32':
            subprocess.run(['taskkill', '/F', '/IM', 'chromedriver.exe'], 
                         capture_output=True, stderr=subprocess.DEVNULL)
            subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], 
                         capture_output=True, stderr=subprocess.DEVNULL)
            time.sleep(1)
    except:
        pass
    
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()
    return driver

def login(driver, email, password):
    """ログイン処理"""
    logging.info("🔐 ログインしています...")
    
    driver.get(URL)
    wait = WebDriverWait(driver, 10)
    
    try:
        email_input = wait.until(
            EC.presence_of_element_located((By.NAME, 'email'))
        )
        email_input.send_keys(email)
        logging.info("✅ メールアドレスを入力しました")
        
        password_input = driver.find_element(By.NAME, 'password')
        password_input.send_keys(password)
        logging.info("✅ パスワードを入力しました")
        
        login_button = driver.find_element(By.XPATH, '//button[contains(text(), "ログイン")]')
        login_button.click()
        logging.info("✅ ログインボタンをクリックしました")
        
        wait.until(
            EC.presence_of_all_elements_located((By.XPATH, '//button[contains(text(), "受講する")]'))
        )
        logging.info("✅ ログイン完了！\n")
        
        return True
    except Exception as e:
        logging.error(f"❌ ログイン処理でエラー: {e}")
        return False

def get_content_list(driver, start_section, end_section):
    """セクション範囲のコンテンツ一覧を取得"""
    logging.info(f"📋 コンテンツ一覧を取得中...")
    
    content_list = []
    try:
        wait = WebDriverWait(driver, 15)
        parent_window = driver.current_window_handle
        
        buttons = driver.find_elements(By.XPATH, '//button[contains(text(), "受講する")]')
        
        for section_num in range(start_section, end_section + 1):
            button_index = section_num - 1
            
            if button_index >= len(buttons):
                logging.warning(f"⚠️ セクション {section_num} のボタンが見つかりません")
                continue
            
            logging.info(f"  セクション {section_num} を確認中...")
            buttons[button_index].click()
            time.sleep(3)
            
            if len(driver.window_handles) > 1:
                driver.switch_to.window(driver.window_handles[-1])
            
            # コンテンツ数をカウント
            content_count = 0
            content_index = 1
            
            while True:
                # 再生ボタンがあるか確認（複数のセレクタを試行）
                play_button_found = False
                play_button_selectors = [
                    '//button[contains(@aria-label, "play") or contains(@aria-label, "再生")]',
                    '//button[@class and contains(@class, "play")]',
                    '//div[contains(@class, "video")]//button',
                    '//div[contains(@class, "player")]//button',
                    '//button[contains(@class, "vjs-big-play-button")]',
                    '//div[@class and contains(@class, "play")]',
                ]
                
                for selector in play_button_selectors:
                    try:
                        WebDriverWait(driver, 3).until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                        play_button_found = True
                        break
                    except:
                        continue
                
                if play_button_found:
                    content_count += 1
                    content_list.append((section_num, content_count))
                    logging.info(f"    コンテンツ {content_count} を検出")
                    
                    # 「次へ」ボタンをクリック
                    next_button_clicked = False
                    next_button_selectors = [
                        '//button[contains(text(), "次へ")]',
                        '//a[contains(text(), "次へ")]',
                        '//button[contains(@class, "next")]',
                        '//a[contains(@class, "next")]',
                    ]
                    
                    for selector in next_button_selectors:
                        try:
                            next_button = WebDriverWait(driver, 3).until(
                                EC.element_to_be_clickable((By.XPATH, selector))
                            )
                            next_button.click()
                            next_button_clicked = True
                            time.sleep(2)
                            break
                        except:
                            continue
                    
                    if not next_button_clicked:
                        logging.info(f"    セクション {section_num} は {content_count} 個のコンテンツで終了")
                        break
                    
                    content_index += 1
                    if content_index > 100:  # 無限ループ防止
                        break
                else:
                    logging.info(f"    セクション {section_num} は {content_count} 個のコンテンツで終了")
                    break
            
            # メインページに戻る
            try:
                driver.back()
                time.sleep(2)
            except:
                pass
            
            if len(driver.window_handles) > 1:
                try:
                    driver.close()
                    driver.switch_to.window(parent_window)
                except:
                    pass
            
            time.sleep(2)
            buttons = driver.find_elements(By.XPATH, '//button[contains(text(), "受講する")]')
        
        return content_list
        
    except Exception as e:
        logging.error(f"❌ コンテンツ一覧取得エラー: {e}")
        return content_list

def play_content_quick(driver, section_index, content_index, test_duration=10, retry_count=3):
    """単一のコンテンツを高速テスト再生（指定秒数だけ再生）"""
    for attempt in range(retry_count):
        try:
            wait = WebDriverWait(driver, 15)
            
            logging.info(f"  🎬 再生ボタンを探してクリック...")
            play_button_clicked = False
            
            play_button_selectors = [
                '//button[contains(@aria-label, "play") or contains(@aria-label, "再生")]',
                '//button[@class and contains(@class, "play")]',
                '//div[contains(@class, "video")]//button',
                '//div[contains(@class, "player")]//button',
                '//button[contains(@class, "vjs-big-play-button")]',
            ]
            
            for selector in play_button_selectors:
                try:
                    play_button = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    play_button.click()
                    logging.info("  ✅ 再生ボタンをクリックしました")
                    play_button_clicked = True
                    time.sleep(3)
                    break
                except:
                    continue
            
            if not play_button_clicked:
                logging.warning("  ⚠️ 再生ボタンが見つかりません")
            
            logging.info(f"  ⏳ {test_duration}秒間再生...")
            
            # iframe切り替え
            try:
                iframes = driver.find_elements(By.TAG_NAME, 'iframe')
                if iframes:
                    driver.switch_to.frame(iframes[0])
                    time.sleep(2)
            except:
                pass
            
            try:
                video = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'video'))
                )
                logging.info("  ✅ ビデオ要素が見つかりました")
                
                try:
                    driver.execute_script("arguments[0].play();", video)
                    logging.info("  ✅ JavaScriptでビデオ再生を開始しました")
                    time.sleep(2)
                except:
                    pass
                
                # 指定時間だけ待機
                elapsed = 0
                start_time = time.time()
                while elapsed < test_duration:
                    try:
                        current_time = video.get_property('currentTime')
                        duration = video.get_property('duration')
                        
                        if duration and current_time is not None:
                            progress = (current_time / duration * 100) if duration > 0 else 0
                            print(f"\r[セクション {section_index} / コンテンツ {content_index}] {int(current_time)}/{int(duration)}秒 ({progress:.1f}%)", end='', flush=True)
                    except:
                        pass
                    
                    time.sleep(1)
                    elapsed = time.time() - start_time
                
                print()  # 改行
                logging.info(f"  ✅ {test_duration}秒間の再生完了")
                
            except Exception as e:
                logging.warning(f"  ⚠️ ビデオ要素エラー: {e}")
            
            # iframe から戻る
            try:
                driver.switch_to.default_content()
            except:
                pass
            
            # 「次へ」ボタンをクリック
            logging.info("  📌 「次へ」ボタンをクリック...")
            
            next_button_selectors = [
                '//button[contains(text(), "次へ")]',
                '//a[contains(text(), "次へ")]',
                '//button[contains(@class, "next")]',
            ]
            
            next_button = None
            for selector in next_button_selectors:
                try:
                    next_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except:
                    continue
            
            if next_button:
                try:
                    next_button.click()
                    logging.info("  ✅ 「次へ」ボタンをクリックしました")
                    time.sleep(3)
                    return True
                except:
                    try:
                        driver.execute_script("arguments[0].click();", next_button)
                        logging.info("  ✅ JavaScriptで「次へ」ボタンをクリックしました")
                        time.sleep(3)
                        return True
                    except:
                        pass
            
            logging.info("  ℹ️ 「次へ」ボタンが見つかりません（セクション終了）")
            return False
                
        except Exception as e:
            if attempt < retry_count - 1:
                logging.warning(f"  ⚠️ エラー（リトライ {attempt + 1}/{retry_count}）: {e}")
                time.sleep(2)
            else:
                logging.error(f"  ❌ エラー: {e}")
                return False
    
    return False

def play_section_quick(driver, section_index, parent_window):
    """セクションを高速テスト再生"""
    logging.info(f"\n{'='*60}")
    logging.info(f"🎬 セクション {section_index} をテスト再生開始")
    logging.info(f"{'='*60}")
    
    try:
        wait = WebDriverWait(driver, 15)
        
        # 「受講する」ボタンをクリック
        buttons = driver.find_elements(By.XPATH, '//button[contains(text(), "受講する")]')
        button_index = section_index - 1
        
        logging.info(f"🔍 ボタンインデックス: {button_index}（{len(buttons)}個中）をクリック")
        
        if button_index < len(buttons):
            buttons[button_index].click()
            logging.info(f"✅ セクション {section_index} の「受講する」ボタンをクリック")
            
            time.sleep(3)
            
            # ウィンドウ切り替え
            if len(driver.window_handles) > 1:
                driver.switch_to.window(driver.window_handles[-1])
                logging.info("✅ コンテンツページに切り替え")
            
            # コンテンツを再生
            content_index = 1
            while True:
                logging.info(f"\n  📝 コンテンツ {content_index} をテスト...")
                
                if play_content_quick(driver, section_index, content_index, TEST_VIDEO_DURATION):
                    content_index += 1
                else:
                    logging.info(f"  ℹ️ コンテンツ {content_index} で終了")
                    break
            
            logging.info(f"\n✅ セクション {section_index} のテスト完了（{content_index - 1}個）")
            
            # メインページに戻る
            logging.info("  🔙 メインページに戻ります...")
            try:
                driver.back()
                logging.info("  ✅ 戻りました")
                time.sleep(2)
            except:
                pass
            
            if len(driver.window_handles) > 1:
                try:
                    driver.close()
                    driver.switch_to.window(parent_window)
                except:
                    pass
            
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
    logging.info("=" * 60)
    logging.info("🧪 クイックテスト版（カスタマイズ可能）")
    logging.info("=" * 60)
    logging.info(f"📋 テスト設定:")
    logging.info(f"   - 各動画: 最初の {TEST_VIDEO_DURATION} 秒だけ再生")
    logging.info(f"   - .env設定に従う")
    logging.info("=" * 60)
    logging.info("")
    
    if not EMAIL or not PASSWORD:
        logging.error("❌ エラー: .env ファイルに認証情報がありません")
        return
    
    # セクション範囲を決定
    start_section = int(START_SECTION) if START_SECTION else 1
    end_section = int(END_SECTION) if END_SECTION else None
    
    logging.info(f"📌 開始セクション: {start_section}")
    if end_section:
        logging.info(f"📌 終了セクション: {end_section}")
    else:
        logging.info(f"📌 終了セクション: 最後まで")
    
    driver = None
    try:
        driver = setup_driver()
        logging.info("✅ ブラウザを起動しました\n")
        
        if not login(driver, EMAIL, PASSWORD):
            logging.error("❌ ログインに失敗しました")
            return
        
        # コンテンツ一覧を取得
        if end_section:
            content_list = get_content_list(driver, start_section, end_section)
        else:
            # 終了セクションが指定されていない場合は、すべてを対象
            buttons = driver.find_elements(By.XPATH, '//button[contains(text(), "受講する")]')
            end_section = len(buttons)
            logging.info(f"📌 終了セクション: {end_section}（全セクション）")
            content_list = get_content_list(driver, start_section, end_section)
        
        # コンテンツ一覧を表示
        logging.info("\n" + "=" * 60)
        logging.info(f"📊 コンテンツ一覧（合計 {len(content_list)} 個）:")
        logging.info("=" * 60)
        for idx, (section, content) in enumerate(content_list, 1):
            print(f"  {idx:3d}: セクション {section} / コンテンツ {content}")
            if idx % 10 == 0:
                logging.info(f"  ... {idx}/{len(content_list)}")
        
        # 再生開始位置を入力
        logging.info("\n" + "=" * 60)
        start_idx = input(f"再生開始位置を入力してください (1-{len(content_list)}) [デフォルト: 1]: ").strip()
        
        if start_idx == "":
            start_idx = 1
        else:
            try:
                start_idx = int(start_idx)
                if start_idx < 1 or start_idx > len(content_list):
                    logging.error(f"❌ 無効な位置です（1-{len(content_list)}）")
                    return
            except ValueError:
                logging.error("❌ 数値を入力してください")
                return
        
        logging.info(f"✅ コンテンツ {start_idx} から再生開始します\n")
        
        parent_window = driver.current_window_handle
        
        # 選択位置から再生開始
        current_content_idx = 1
        for section_num in range(start_section, end_section + 1):
            section_contents = [c for c in content_list if c[0] == section_num]
            
            for content_num in range(1, len(section_contents) + 1):
                if current_content_idx < start_idx:
                    current_content_idx += 1
                    continue
                
                if play_section_quick(driver, section_num, parent_window):
                    logging.info(f"✅ セクション {section_num} テスト完了")
                else:
                    logging.warning(f"⚠️ セクション {section_num} テスト失敗")
                break  # セクション内の1つのコンテンツだけテスト
        
        logging.info("\n" + "=" * 60)
        logging.info("✅ テスト完了！")
        logging.info("=" * 60)
        logging.info(f"📄 ログファイル: {LOG_FILE}")
        
    except KeyboardInterrupt:
        logging.info("\n⚠️ ユーザーによって中断されました")
    except Exception as e:
        logging.error(f"❌ 予期しないエラー: {e}")
        import traceback
        logging.error(traceback.format_exc())
    finally:
        if driver:
            try:
                driver.quit()
                logging.info("✅ ブラウザを閉じました")
            except:
                pass

if __name__ == '__main__':
    main()
