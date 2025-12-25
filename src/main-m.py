"""
Contents Engine マスタープログラム - セクション/コンテンツリスト取得版

各セクションを順番に開いて、コンテンツのタイトルを取得し、CSVに保存
"""

import os
import sys
import time
import csv
import logging
from datetime import datetime
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Windowsコンソール対応
if sys.platform == 'win32':
    try:
        import subprocess
        subprocess.run(['chcp', '65001'], shell=True, capture_output=True)
    except:
        pass
    import builtins
    _original_print = builtins.print
    def safe_print(*args, **kwargs):
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

load_dotenv()

EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
URL = 'https://letter.the-3rd-brain.com/members/C3sxfGdWUas4/course/UZr4qDbqxh9I'
LOG_FILE = f'content_list_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
CSV_FILE = f'content_list_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(LOG_FILE, encoding='utf-8'), logging.StreamHandler()]
)

def setup_driver():
    """Chromeドライバーをセットアップ"""
    try:
        import subprocess
        if sys.platform == 'win32':
            subprocess.run(['taskkill', '/F', '/IM', 'chromedriver.exe'], capture_output=True, stderr=subprocess.DEVNULL)
            subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], capture_output=True, stderr=subprocess.DEVNULL)
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
    logging.info("ログインしています...")
    driver.get(URL)
    wait = WebDriverWait(driver, 10)
    
    try:
        email_input = wait.until(EC.presence_of_element_located((By.NAME, 'email')))
        email_input.send_keys(email)
        
        password_input = driver.find_element(By.NAME, 'password')
        password_input.send_keys(password)
        
        login_button = driver.find_element(By.XPATH, '//button[contains(text(), "ログイン")]')
        login_button.click()
        
        wait.until(EC.presence_of_all_elements_located((By.XPATH, '//button[contains(text(), "受講する")]')))
        logging.info("ログイン完了！")
        return True
    except Exception as e:
        logging.error(f"ログインエラー: {e}")
        return False

def get_section_content(driver, section_num, section_button):
    """セクション内のコンテンツを取得"""
    contents = []
    parent_window = driver.current_window_handle
    
    try:
        # セクションをクリック
        section_button.click()
        time.sleep(2)
        
        # ウィンドウ切り替え
        if len(driver.window_handles) > 1:
            driver.switch_to.window(driver.window_handles[-1])
        
        time.sleep(1)
        
        # コンテンツのタイトルを取得
        # 複数の要素タイプをチェック
        selectors = [
            '//li[contains(@class, "step")]',
            '//div[contains(@class, "lesson-item")]',
            '//div[contains(@class, "content")]//h3',
            '//div[contains(@class, "content")]//h2',
            '//li',
        ]
        
        found_contents = set()
        
        for selector in selectors:
            try:
                elements = driver.find_elements(By.XPATH, selector)
                for elem in elements:
                    text = elem.text.strip()
                    # フィルタリング：有効なテキストのみ
                    if text and len(text) > 2 and len(text) < 200 and text not in found_contents:
                        # 重複を避ける
                        found_contents.add(text)
                        contents.append(text)
                        
                        # 最大50個まで取得
                        if len(contents) >= 50:
                            break
            except:
                continue
            
            if len(contents) >= 50:
                break
        
        # メインページに戻る
        driver.back()
        time.sleep(1)
        
        # ウィンドウ切り替え
        if len(driver.window_handles) > 1:
            try:
                driver.close()
            except:
                pass
        driver.switch_to.window(parent_window)
        time.sleep(1)
        
        # セクション一覧を再取得
        try:
            WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located((By.XPATH, '//button[contains(text(), "受講する")]'))
            )
        except:
            pass
        
    except Exception as e:
        logging.error(f"セクション {section_num} コンテンツ取得エラー: {e}")
        try:
            driver.back()
            if len(driver.window_handles) > 1:
                try:
                    driver.close()
                except:
                    pass
            driver.switch_to.window(parent_window)
        except:
            pass
    
    return contents

def main():
    """メイン処理"""
    driver = None
    all_data = []  # CSV保存用
    
    try:
        driver = setup_driver()
        logging.info("ブラウザを起動しました\n")
        
        if not login(driver, EMAIL, PASSWORD):
            logging.error("ログインに失敗しました")
            return
        
        # セクション一覧を取得
        buttons = driver.find_elements(By.XPATH, '//button[contains(text(), "受講する")]')
        total_sections = len(buttons)
        
        print(f"\n{'='*80}")
        print(f"セクション・コンテンツ一覧取得開始")
        print(f"全セクション数: {total_sections} 個")
        print(f"{'='*80}\n")
        logging.info(f"全セクション数: {total_sections} 個")
        
        # CSVヘッダーを設定
        csv_headers = ['セクション番号', 'セクション名', 'コンテンツ番号', 'コンテンツ名']
        
        # 各セクションを処理
        for section_num in range(1, total_sections + 1):
            try:
                # セクション一覧を再取得（ボタンが新しくなっている可能性）
                buttons = driver.find_elements(By.XPATH, '//button[contains(text(), "受講する")]')
                
                if section_num > len(buttons):
                    logging.warning(f"セクション {section_num}: ボタンが見つかりません")
                    break
                
                button = buttons[section_num - 1]
                
                # セクション名を取得
                parent_elem = button.find_element(By.XPATH, '..')
                section_name = parent_elem.text.strip()
                if '受講する' in section_name:
                    section_name = section_name.replace('受講する', '').strip()
                if not section_name:
                    section_name = f"セクション {section_num}"
                
                print(f"セクション {section_num:2d}: {section_name}")
                logging.info(f"セクション {section_num:2d}: {section_name}")
                
                # コンテンツを取得
                contents = get_section_content(driver, section_num, button)
                
                if contents:
                    print(f"  → コンテンツ {len(contents)} 個を取得")
                    logging.info(f"  → コンテンツ {len(contents)} 個を取得")
                    
                    for content_num, content_name in enumerate(contents, 1):
                        all_data.append([section_num, section_name, content_num, content_name])
                        print(f"    {content_num:2d}. {content_name[:60]}")
                        logging.info(f"    {content_num:2d}. {content_name[:60]}")
                else:
                    print(f"  → コンテンツなし")
                    logging.info(f"  → コンテンツなし")
                    all_data.append([section_num, section_name, 0, "(コンテンツなし)"])
                
                print()
                
            except Exception as e:
                logging.error(f"セクション {section_num} 処理エラー: {e}")
                print(f"セクション {section_num}: エラーが発生しました")
                continue
        
        # CSVファイルに保存
        print(f"\n{'='*80}")
        print(f"CSVファイルに保存中...")
        
        try:
            with open(CSV_FILE, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(csv_headers)
                writer.writerows(all_data)
            
            print(f"保存完了: {CSV_FILE}")
            logging.info(f"CSVファイル保存: {CSV_FILE}")
        except Exception as e:
            logging.error(f"CSV保存エラー: {e}")
            print(f"CSV保存エラー: {e}")
        
        print(f"ログファイル: {LOG_FILE}")
        print(f"{'='*80}\n")
        
        logging.info(f"処理完了！")
        logging.info(f"ファイル保存先:")
        logging.info(f"  CSV: {CSV_FILE}")
        logging.info(f"  LOG: {LOG_FILE}")
        
    except Exception as e:
        logging.error(f"エラーが発生しました: {e}")
        import traceback
        logging.error(traceback.format_exc())
    finally:
        if driver:
            try:
                driver.quit()
                logging.info("ブラウザを閉じました")
            except:
                pass

if __name__ == '__main__':
    main()

