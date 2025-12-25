"""
ブラウザ起動テスト - Chromeが正常に開くかだけを確認
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

print("🚀 Chromeブラウザを起動します...")

try:
    # Chromeドライバーをセットアップ
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()
    
    print("✅ Chromeブラウザが起動しました！")
    print("🌐 Googleにアクセスします...")
    
    driver.get("https://www.google.com")
    
    print("✅ Googleにアクセスできました！")
    print("\n✋ Enterキーを押すとブラウザを閉じます...")
    
    input()
    
    driver.quit()
    print("✅ ブラウザを閉じました")
    
except Exception as e:
    print(f"❌ エラーが発生しました: {e}")
    import traceback
    traceback.print_exc()

