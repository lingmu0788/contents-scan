"""
「次へ」ボタンの動作確認テスト

ビデオ再生中でも「次へ」ボタンがクリック可能か確認するシンプルなテスト
"""

import os
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

# .env ファイルから環境変数を読み込む
load_dotenv()

# 設定値
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
URL = 'https://letter.the-3rd-brain.com/members/C3sxfGdWUas4/course/UZr4qDbqxh9I'
LOG_FILE = f'test_next_button_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

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
        logging.info("✅ ログイン完了！セクション一覧が表示されました\n")
        
        return True
    except Exception as e:
        logging.error(f"❌ ログイン処理でエラーが発生しました: {e}")
        return False

def test_next_button(driver):
    """「次へ」ボタンの動作確認"""
    logging.info("\n" + "=" * 60)
    logging.info("🧪 「次へ」ボタンの動作確認テスト")
    logging.info("=" * 60)
    
    try:
        wait = WebDriverWait(driver, 15)
        
        # 1. セクション1の「受講する」ボタンをクリック
        logging.info("\n📌 ステップ1: セクション1を開く")
        buttons = driver.find_elements(By.XPATH, '//button[contains(text(), "受講する")]')
        if len(buttons) < 1:
            logging.error("❌ セクション1が見つかりません")
            return False
        
        buttons[0].click()
        logging.info("✅ セクション1の「受講する」ボタンをクリックしました")
        
        # ページ遷移待機
        logging.info("⏳ ページ遷移を待機中...")
        time.sleep(8)
        
        current_url = driver.current_url
        logging.info(f"📍 現在のURL: {current_url}")
        
        # 2. iframe に切り替えてビデオを再生開始
        logging.info("\n📌 ステップ2: ビデオを再生開始")
        iframes = driver.find_elements(By.TAG_NAME, 'iframe')
        if iframes:
            logging.info(f"🔍 iframe を発見しました（{len(iframes)}個）")
            driver.switch_to.frame(iframes[0])
            logging.info("✅ iframe に切り替えました")
            time.sleep(2)
        
        # ビデオ要素を探す
        video = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, 'video'))
        )
        logging.info("✅ ビデオ要素が見つかりました")
        
        # ビデオを再生開始
        driver.execute_script("arguments[0].play();", video)
        logging.info("✅ JavaScriptでビデオ再生を開始しました")
        time.sleep(5)  # 再生開始を待つ
        
        # ビデオが再生中か確認
        current_time = video.get_property('currentTime')
        duration = video.get_property('duration')
        logging.info(f"⏱️  ビデオ再生中: {int(current_time)}/{int(duration)}秒")
        
        # 3. iframe から戻る
        logging.info("\n📌 ステップ3: iframe から戻る")
        driver.switch_to.default_content()
        logging.info("✅ iframe からメインコンテンツに戻りました")
        time.sleep(2)
        
        # 4. 「次へ」ボタンを探す（ビデオ再生中）
        logging.info("\n📌 ステップ4: 「次へ」ボタンを探す（ビデオ再生中）")
        
        # デバッグ：ページ内のボタンを確認
        all_buttons = driver.find_elements(By.TAG_NAME, 'button')
        logging.info(f"🔍 ページ内のボタン数: {len(all_buttons)}")
        
        next_button_found = False
        next_button_text = None
        
        for i, btn in enumerate(all_buttons):
            try:
                btn_text = btn.text.strip()
                if btn_text and ('次へ' in btn_text or 'next' in btn_text.lower()):
                    logging.info(f"  ✅ 「次へ」ボタンを発見: '{btn_text}' (ボタン {i+1})")
                    next_button_found = True
                    next_button_text = btn_text
                    break
            except:
                continue
        
        if not next_button_found:
            # リンクも確認
            all_links = driver.find_elements(By.TAG_NAME, 'a')
            logging.info(f"🔍 ページ内のリンク数: {len(all_links)}")
            for i, link in enumerate(all_links):
                try:
                    link_text = link.text.strip()
                    if link_text and ('次へ' in link_text or 'next' in link_text.lower()):
                        logging.info(f"  ✅ 「次へ」リンクを発見: '{link_text}' (リンク {i+1})")
                        next_button_found = True
                        next_button_text = link_text
                        break
                except:
                    continue
        
        # 5. 「次へ」ボタンをクリックしてみる
        logging.info("\n📌 ステップ5: 「次へ」ボタンをクリック（ビデオ再生中）")
        
        if next_button_found:
            # 複数のセレクタパターンを試行
            next_button_selectors = [
                f'//button[contains(text(), "{next_button_text}")]',
                f'//a[contains(text(), "{next_button_text}")]',
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
                    logging.info(f"✅ 「次へ」ボタン要素を取得しました（セレクタ: {selector}）")
                    break
                except:
                    continue
            
            if next_button:
                try:
                    # 通常のクリックを試みる
                    next_button.click()
                    logging.info("✅ 「次へ」ボタンをクリックしました（通常のクリック）")
                    time.sleep(3)
                    
                    # ページ遷移を確認
                    new_url = driver.current_url
                    if new_url != current_url:
                        logging.info(f"✅ ページ遷移成功！新しいURL: {new_url}")
                        logging.info("🎉 「次へ」ボタンはビデオ再生中でもクリック可能です！")
                        return True
                    else:
                        logging.warning("⚠️ ページ遷移が確認できませんでした")
                        return False
                        
                except Exception as click_e:
                    logging.warning(f"⚠️ 通常のクリックエラー: {click_e}")
                    # JavaScriptでクリックを試みる
                    try:
                        driver.execute_script("arguments[0].click();", next_button)
                        logging.info("✅ 「次へ」ボタンをクリックしました（JavaScript）")
                        time.sleep(3)
                        
                        new_url = driver.current_url
                        if new_url != current_url:
                            logging.info(f"✅ ページ遷移成功！新しいURL: {new_url}")
                            logging.info("🎉 「次へ」ボタンはビデオ再生中でもクリック可能です！")
                            return True
                        else:
                            logging.warning("⚠️ ページ遷移が確認できませんでした")
                            return False
                    except Exception as js_e:
                        logging.error(f"❌ JavaScriptクリックエラー: {js_e}")
                        return False
            else:
                logging.error("❌ 「次へ」ボタン要素を取得できませんでした")
                return False
        else:
            logging.error("❌ 「次へ」ボタンが見つかりませんでした")
            return False
            
    except Exception as e:
        logging.error(f"❌ テストエラー: {e}")
        import traceback
        logging.error(traceback.format_exc())
        return False

def main():
    """メイン処理"""
    logging.info("=" * 60)
    logging.info("🧪 「次へ」ボタンの動作確認テスト")
    logging.info("=" * 60)
    logging.info("")
    
    if not EMAIL or not PASSWORD:
        logging.error("❌ エラー: .env ファイルにメールアドレスとパスワードが設定されていません")
        return
    
    driver = None
    try:
        driver = setup_driver()
        logging.info("✅ ブラウザを起動しました\n")
        
        if not login(driver, EMAIL, PASSWORD):
            logging.error("❌ ログインに失敗しました")
            return
        
        # 「次へ」ボタンの動作確認
        if test_next_button(driver):
            logging.info("\n" + "=" * 60)
            logging.info("✅ テスト成功！「次へ」ボタンはビデオ再生中でもクリック可能です！")
            logging.info("=" * 60)
        else:
            logging.error("\n" + "=" * 60)
            logging.error("❌ テスト失敗")
            logging.error("=" * 60)
        
    except KeyboardInterrupt:
        logging.info("\n⚠️ ユーザーによって中断されました")
    except Exception as e:
        logging.error(f"❌ 予期しないエラーが発生しました: {e}")
        import traceback
        logging.error(traceback.format_exc())
    finally:
        if driver:
            try:
                input("\n✋ Enterキーを押すとブラウザを閉じます...")
                driver.quit()
                logging.info("✅ ブラウザを閉じました")
            except:
                pass

if __name__ == '__main__':
    main()

