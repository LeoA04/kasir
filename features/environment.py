from os import getenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoAlertPresentException
import requests
import time

# =========================
# KONFIGURASI DASAR
# =========================
BASE_URL = getenv("BASE_URL", "http://127.0.0.1:5000")
WAIT_SECONDS = int(getenv("WAIT_SECONDS", "10"))

# =========================
# HOOKS BEHAVE
# =========================
def before_all(context):
    """
    Dijalanan sekali sebelum seluruh test dieksekusi
    """
    context.base_url = BASE_URL
    context.wait_seconds = WAIT_SECONDS

    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--headless")  # aman untuk CI / lab
    chrome_options.add_argument("--window-size=1920,1080")

    # Inisialisasi WebDriver
    context.driver = webdriver.Chrome(options=chrome_options)
    context.driver.implicitly_wait(context.wait_seconds)

    print("\n[SETUP] Browser initialized")
    print(f"[SETUP] Base URL: {context.base_url}")

    # OPTIONAL: reset kondisi test (jika endpoint tersedia)
    try:
        requests.post(f"{BASE_URL}/pets/reset")
        print("[SETUP] Test data reset")
    except Exception:
        print("[SETUP] No reset endpoint, skipping")


def before_scenario(context, scenario):
    """
    Dijalankan sebelum setiap scenario
    """
    print(f"\n[SCENARIO START] {scenario.name}")


def after_scenario(context, scenario):
    try:
        alert = context.driver.switch_to.alert
        alert.accept()
    except NoAlertPresentException:
        pass

    context.driver.delete_all_cookies()


def after_all(context):
    """
    Dijalanan sekali setelah semua test selesai
    """
    context.driver.quit()
    print("\n[TEARDOWN] Browser closed")
