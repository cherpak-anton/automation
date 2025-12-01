import json
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright
import time, random
from data.config import *
from utils.utils import (load_accounts,
                        ro_fetch_methods,
                        ro_log_changes,
                        load_golden_data,
                        update_golden_file,
                        save_golden_data,
                        ro_refresh_methods,
                        launch_browser)

# === PLAYWRIGHT ===
def run_playwright(username, password, headless=True):
    # this sleep to avoid being detected as bot
    time.sleep(random.randint(30, 60))
    page, browser, p = launch_browser(headless=headless)
    page.goto(CJ_URL, timeout=90000)
    page.wait_for_selector(CJ_LOGIN_BUTTON, timeout=60000)
    page.locator(CJ_LOGIN_BUTTON).click()

    # login
    page.locator(CJ_USERNAME_FIELD).fill(username)
    page.locator(CJ_PASSWORD_FIELD).fill(password)
    time.sleep(2)
    page.locator(CJ_SUBMIT_BUTTON).click()

    # --- payment methods ---
    page.locator(CJ_DEPOSIT_BUTTON_SELECTOR).click()
    time.sleep(5)
    payment_methods = ro_fetch_methods(page, CJ_LIST_OF_METHODS_SELECTOR,"payment")

    # --- withdraw methods ---
    page.locator(CJ_WITHDRAW_BUTTON_SELECTOR).click()
    time.sleep(5)
    withdraw_methods = ro_fetch_methods(page, CJ_LIST_OF_METHODS_SELECTOR, "withdraw")

    browser.close()
    p.stop()
    return payment_methods, withdraw_methods

def main(headless=True):
    accounts = load_accounts()
    if not accounts:
        print("No accounts to process.")
        return

    site_name = "Casinojoy"
    site_accounts = accounts.get(site_name, {})

    golden_data = load_golden_data(GOLDEN_JSON_FILE)

    new_project, changes_per_country = ro_refresh_methods(
        site_name,
        site_accounts,
        golden_data,
        run_func=run_playwright, 
        headless=headless
    )

    ro_log_changes(changes_per_country, CJ_LOG_FILE)
    update_golden_file(golden_data, new_project, site_name)
    save_golden_data(golden_data, GOLDEN_JSON_FILE)

    print(f"Done. Golden ref: {GOLDEN_JSON_FILE.name}, log: {CJ_LOG_FILE.name}")


if __name__ == "__main__":
    main(headless=True)
