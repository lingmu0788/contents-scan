"""
セクション一覧高速取得スクリプト（改善版）
全セクションの名前をJavaScriptで高速取得
"""

import os
import sys
import time
import logging
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
LOG_FILE = f'section_list_{time.strftime("%Y%m%d_%H%M%S")}.log'

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

def main():
    """メイン処理"""
    driver = None
    try:
        driver = setup_driver()
        logging.info("ブラウザを起動しました\n")
        
        if not login(driver, EMAIL, PASSWORD):
            logging.error("ログインに失敗しました")
            return
        
        # JavaScriptでセクション情報を一括取得
        script = """
        const sections = [];
        // 「受講する」ボタンを全て取得
        const buttons = document.querySelectorAll('button');
        
        for (let i = 0; i < buttons.length; i++) {
            const btn = buttons[i];
            if (btn.textContent.includes('受講する')) {
                // ボタンの親要素から上に遡ってセクション名を探す
                let parent = btn.parentElement;
                let sectionName = '';
                
                // 最大5レベル上まで探す
                for (let j = 0; j < 5 && parent; j++) {
                    const text = parent.textContent.trim();
                    // テキストから「受講する」を除去
                    sectionName = text.replace(/受講する/g, '').trim();
                    
                    // 適切な長さのテキストが見つかったら停止
                    if (sectionName && sectionName.length > 5 && sectionName.length < 200) {
                        break;
                    }
                    parent = parent.parentElement;
                }
                
                // セクション名が見つからない場合のフォールバック
                if (!sectionName || sectionName.length < 3) {
                    // h2, h3などのタイトルを探す
                    const container = btn.closest('div');
                    if (container) {
                        const heading = container.querySelector('h2, h3, h4, .section-title, [class*="title"]');
                        if (heading) {
                            sectionName = heading.textContent.trim();
                        }
                    }
                }
                
                sections.push(sectionName || `セクション ${sections.length + 1}`);
            }
        }
        
        return sections;
        """
        
        sections = driver.execute_script(script)
        total_sections = len(sections)
        
        print(f"\n{'='*60}")
        print(f"📊 全セクション数: {total_sections} 個")
        print(f"{'='*60}\n")
        logging.info(f"📊 全セクション数: {total_sections} 個")
        
        print(f"{'='*60}")
        print("📋 セクション一覧")
        print(f"{'='*60}\n")
        logging.info("📋 セクション一覧:")
        
        for idx, section_name in enumerate(sections, 1):
            print(f"セクション {idx:2d}: {section_name}")
            logging.info(f"セクション {idx:2d}: {section_name}")
        
        print(f"\n{'='*60}")
        print(f"✅ 完了！ {total_sections} 個のセクションを取得しました。")
        print(f"{'='*60}\n")
        
        logging.info(f"\n✅ 完了！ {total_sections} 個のセクションを取得しました。")
        
        # セクション情報をCSVファイルに保存
        csv_file = f'section_list_{time.strftime("%Y%m%d_%H%M%S")}.csv'
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write('セクション番号,セクション名\n')
            for idx, section_name in enumerate(sections, 1):
                f.write(f'{idx},"{section_name}"\n')
        
        print(f"📄 セクション情報を {csv_file} に保存しました。")
        logging.info(f"📄 セクション情報を {csv_file} に保存しました。")
        
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
