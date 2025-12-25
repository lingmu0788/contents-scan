"""
Contents Engine マスタープログラム（Hitomi）自動化スクリプト - テスト版

【テスト版の制限】
- 最初の1セクションのみ実行
- 各ビデオを30秒間だけ再生してスキップ
- 最大2コンテンツまでテスト
- 動作確認用
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
LOG_FILE = f'test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

# テスト設定
MAX_TEST_CONTENTS = 2      # 最大2コンテンツまでテスト
TEST_SECTION_INDEX = 1     # テストするセクション番号
# 注意: ビデオは最後まで再生されます（「次へ」ボタンの動作確認のため）

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
    # options.add_argument('--headless')  # テスト時は画面を見たいのでコメントアウト
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

def play_content_test(driver, content_index):
    """単一のコンテンツをテスト再生（30秒間のみ）"""
    try:
        wait = WebDriverWait(driver, 15)
        
        logging.info(f"  🎬 コンテンツ {content_index} のテスト再生開始...")
        
        # 1. 再生ボタンを検索してクリック
        logging.info("  📍 再生ボタンを探してクリック...")
        play_button_clicked = False
        
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
            logging.warning("  ⚠️ 再生ボタンが見つかりません（自動再生の可能性）")
        
        # 2. ビデオを最後まで再生（「次へ」ボタンの動作確認のため）
        logging.info(f"  ⏳ ビデオを最後まで再生します（「次へ」ボタンの動作確認）...")
        
        # ページ読み込み完了を待つ
        logging.info("  ⏳ ビデオプレイヤーの読み込みを待機中...")
        time.sleep(5)
        
        # デバッグ：現在のURL確認
        current_url = driver.current_url
        logging.info(f"  📍 コンテンツページURL: {current_url}")
        
        # デバッグ：ページタイトル確認
        page_title = driver.title
        logging.info(f"  📄 ページタイトル: {page_title}")
        
        try:
            # iframeがあるか確認
            iframes = driver.find_elements(By.TAG_NAME, 'iframe')
            if iframes:
                logging.info(f"  🔍 iframe を発見しました（{len(iframes)}個）、切り替えます...")
                # 最初のiframeに切り替え
                driver.switch_to.frame(iframes[0])
                logging.info("  ✅ iframe に切り替えました")
                time.sleep(2)
            
            # より長いタイムアウトでビデオ要素を探す
            video = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.TAG_NAME, 'video'))
            )
            logging.info("  ✅ ビデオ要素が見つかりました")
            
            # iframe内で再生ボタンをクリック
            logging.info("  🎬 iframe内で再生ボタンを探しています...")
            time.sleep(2)
            
            # JavaScriptで直接再生を試みる
            try:
                driver.execute_script("arguments[0].play();", video)
                logging.info("  ✅ JavaScriptでビデオ再生を開始しました")
                time.sleep(3)  # 再生開始を待つ
            except Exception as play_e:
                logging.warning(f"  ⚠️ JavaScript再生エラー: {play_e}")
                
                # 再生ボタンを探してクリックする方法も試す
                try:
                    # iframe内の再生ボタンを探す
                    play_button_selectors = [
                        '//button[contains(@aria-label, "play") or contains(@aria-label, "再生")]',
                        '//button[@class and contains(@class, "play")]',
                        '//div[contains(@class, "play")]',
                        '//button[contains(@class, "vjs-big-play-button")]',
                    ]
                    
                    button_clicked = False
                    for selector in play_button_selectors:
                        try:
                            play_btn = WebDriverWait(driver, 3).until(
                                EC.element_to_be_clickable((By.XPATH, selector))
                            )
                            play_btn.click()
                            logging.info(f"  ✅ iframe内の再生ボタンをクリックしました")
                            button_clicked = True
                            time.sleep(3)
                            break
                        except:
                            continue
                    
                    if not button_clicked:
                        logging.warning("  ⚠️ iframe内の再生ボタンが見つかりませんでした")
                except Exception as btn_e:
                    logging.warning(f"  ⚠️ 再生ボタンクリックエラー: {btn_e}")
            
            # ビデオ終了まで監視（「次へ」ボタンの動作確認のため）
            logging.info("  ⏳ ビデオ終了まで待機中...")
            max_wait = 600  # 最大10分（テスト用）
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
                            logging.info(f"  ⏱️  再生中: {int(current_time)}/{int(duration)}秒 ({progress:.1f}%)")
                        
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
                            break
                except Exception as e:
                    logging.debug(f"  ビデオ状態チェック中: {e}")
                
                time.sleep(1)
                elapsed += 1
            
            if elapsed >= max_wait:
                logging.warning(f"  ⚠️ 最大待機時間に達しました（{max_wait}秒）")
            else:
                logging.info(f"  ⏹️  ビデオ再生完了（{elapsed}秒待機）")
                
        except Exception as e:
            logging.warning(f"  ⚠️ ビデオ要素が見つかりません: {e}")
            
            # デバッグ：ページのHTMLを確認
            try:
                page_source_snippet = driver.page_source[:1000]
                logging.info(f"  🔍 ページHTML（最初の1000文字）: {page_source_snippet}")
                
                # iframe があるか確認
                iframes = driver.find_elements(By.TAG_NAME, 'iframe')
                logging.info(f"  🔍 iframeの数: {len(iframes)}")
                
                # div要素があるか確認
                video_containers = driver.find_elements(By.XPATH, '//div[contains(@class, "video") or contains(@class, "player")]')
                logging.info(f"  🔍 video/player クラスのdiv数: {len(video_containers)}")
            except Exception as debug_e:
                logging.warning(f"  ⚠️ デバッグ情報取得エラー: {debug_e}")
        
        # iframeから戻る
        try:
            driver.switch_to.default_content()
            logging.info("  🔙 iframeからメインコンテンツに戻りました")
        except:
            pass
        
        # 3. 「次へ」ボタンをクリック（あれば）
        # iframeから戻っていることを確認
        try:
            driver.switch_to.default_content()
            logging.info("  🔙 iframeからメインコンテンツに戻りました（確認）")
        except:
            pass
        
        logging.info("  📌 「次へ」ボタンを探しています...")
        
        # まず、ページ内のすべてのボタンとリンクを確認して「次へ」を含むものを探す
        next_button_text = None
        next_button_found = False
        
        try:
            all_buttons = driver.find_elements(By.TAG_NAME, 'button')
            logging.info(f"  🔍 ページ内のボタン数: {len(all_buttons)}")
            for i, btn in enumerate(all_buttons):
                try:
                    btn_text = btn.text.strip()
                    if btn_text and ('次へ' in btn_text or 'next' in btn_text.lower()):
                        logging.info(f"  ✅ 「次へ」ボタンを発見: '{btn_text}' (ボタン {i+1})")
                        next_button_text = btn_text
                        next_button_found = True
                        break
                except:
                    continue
            
            if not next_button_found:
                all_links = driver.find_elements(By.TAG_NAME, 'a')
                logging.info(f"  🔍 ページ内のリンク数: {len(all_links)}")
                for i, link in enumerate(all_links):
                    try:
                        link_text = link.text.strip()
                        if link_text and ('次へ' in link_text or 'next' in link_text.lower()):
                            logging.info(f"  ✅ 「次へ」リンクを発見: '{link_text}' (リンク {i+1})")
                            next_button_text = link_text
                            next_button_found = True
                            break
                    except:
                        continue
        except Exception as debug_e:
            logging.warning(f"  ⚠️ デバッグ情報取得エラー: {debug_e}")
        
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
                logging.info(f"  ✅ 「次へ」ボタン要素を取得しました（セレクタ: {selector}）")
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
        
        logging.info(f"  ℹ️ 「次へ」ボタンが見つかりません（セクション終了の可能性）")
        return False
            
    except Exception as e:
        logging.error(f"  ❌ コンテンツ再生エラー: {e}")
        return False

def test_section(driver):
    """最初のセクションをテスト"""
    logging.info(f"\n{'='*60}")
    logging.info(f"🧪 テストモード: セクション {TEST_SECTION_INDEX} を実行")
    logging.info(f"   最大 {MAX_TEST_CONTENTS} コンテンツまでテスト")
    logging.info(f"   各ビデオ: 最後まで完全再生（「次へ」ボタンの動作確認）")
    logging.info(f"{'='*60}")
    
    try:
        wait = WebDriverWait(driver, 15)
        parent_window = driver.current_window_handle
        
        # 「受講する」ボタンをクリック
        buttons = driver.find_elements(By.XPATH, '//button[contains(text(), "受講する")]')
        
        if len(buttons) < TEST_SECTION_INDEX:
            logging.error(f"❌ セクション {TEST_SECTION_INDEX} が見つかりません")
            return False
        
        buttons[TEST_SECTION_INDEX - 1].click()
        logging.info(f"✅ セクション {TEST_SECTION_INDEX} の「受講する」ボタンをクリックしました")
        
        # ページ遷移待機（長めに）
        logging.info("⏳ ページ遷移を待機中...")
        time.sleep(8)
        
        # 現在のURL確認
        current_url = driver.current_url
        logging.info(f"📍 現在のURL: {current_url}")
        
        # ウィンドウ切り替え
        window_count = len(driver.window_handles)
        logging.info(f"📊 ウィンドウ数: {window_count}")
        
        if window_count > 1:
            driver.switch_to.window(driver.window_handles[-1])
            logging.info("✅ コンテンツページに切り替えました")
            time.sleep(3)
            current_url = driver.current_url
            logging.info(f"📍 切り替え後のURL: {current_url}")
        
        # コンテンツをテスト
        content_index = 1
        
        while content_index <= MAX_TEST_CONTENTS:
            logging.info(f"\n  📝 コンテンツ {content_index}/{MAX_TEST_CONTENTS} をテスト...")
            
            if play_content_test(driver, content_index):
                content_index += 1
            else:
                logging.info(f"\n  ℹ️ コンテンツ {content_index} で終了（「次へ」ボタンなし）")
                break
        
        logging.info(f"\n✅ テスト完了！（{content_index - 1}個のコンテンツをテストしました）")
        
        # メインページに戻る
        logging.info("  🔙 メインページに戻ります...")
        try:
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
                driver.back()
                logging.info("  ✅ ブラウザの戻る機能を使用しました")
                time.sleep(2)
                
        except Exception as e:
            logging.warning(f"  ⚠️ 戻る操作エラー: {e}")
        
        if len(driver.window_handles) > 1:
            try:
                driver.close()
                driver.switch_to.window(parent_window)
            except:
                pass
        
        try:
            wait.until(
                EC.presence_of_all_elements_located((By.XPATH, '//button[contains(text(), "受講する")]'))
            )
            logging.info("✅ メインページに戻りました\n")
        except:
            logging.warning("⚠️ メインページの確認ができませんでした")
        
        return True
            
    except Exception as e:
        logging.error(f"❌ テスト実行エラー: {e}")
        try:
            if len(driver.window_handles) > 1:
                driver.close()
            driver.switch_to.window(parent_window)
        except:
            pass
        return False

def main():
    """メイン処理（テスト版）"""
    logging.info("=" * 60)
    logging.info("🧪 Contents Engine 自動化ツール - テスト版")
    logging.info("=" * 60)
    logging.info(f"📋 テスト設定:")
    logging.info(f"   - セクション: {TEST_SECTION_INDEX} のみ")
    logging.info(f"   - コンテンツ: 最大 {MAX_TEST_CONTENTS} 個")
    logging.info(f"   - 再生時間: ビデオを最後まで再生（「次へ」ボタンの動作確認）")
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
        
        # テスト実行
        if test_section(driver):
            logging.info("\n" + "=" * 60)
            logging.info("✅ テストが正常に完了しました！")
            logging.info("=" * 60)
            logging.info(f"📄 ログファイル: {LOG_FILE}")
            logging.info("")
            logging.info("💡 本番実行する場合は以下を実行してください:")
            logging.info("   python main.py")
            logging.info("=" * 60)
        else:
            logging.error("\n❌ テストが失敗しました")
        
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

