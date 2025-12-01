import time, random
from data.config import *
from utils.utils import (load_accounts,
                         launch_browser,
                         load_golden_data,
                         ro_log_changes,
                         ro_fetch_methods,
                         save_golden_data,
                         update_golden_file,
                         ro_refresh_methods)

def run_playwright(username, password, headless=True):
    # this sleep to avoid being detected as bot
    time.sleep(random.randint(30, 60))
    page, browser, p = launch_browser(headless=headless)

    page.goto(RO_URL, timeout=90000)
    page.wait_for_selector(RO_LOGIN_BUTTON, timeout=60000)
    page.locator(RO_LOGIN_BUTTON).click()

    # login
    page.locator(RO_USERNAME_FIELD).fill(username)
    page.locator(RO_PASSWORD_FIELD).fill(password)
    time.sleep(2)
    page.locator(RO_SUBMIT_BUTTON).click()

    # --- payment methods ---
    page.locator(RO_DEPOSIT_BUTTON_SELECTOR).click()
    page.wait_for_url(RO_DEPOSIT_URL, timeout=30000)
    time.sleep(5)
    payment_methods = ro_fetch_methods(page, RO_LIST_OF_METHODS_SELECTOR, "payment")

    # --- withdraw methods ---
    page.locator(RO_WITHDRAW_BUTTON_SELECTOR).click(force=True)
    page.wait_for_url(RO_WITHDRAWAL_URL, timeout=30000)
    time.sleep(5)
    withdraw_methods = ro_fetch_methods(page, RO_LIST_OF_METHODS_SELECTOR, "withdraw")

    browser.close()
    p.stop()
    return payment_methods, withdraw_methods

def main(headless=True):
    accounts = load_accounts()
    if not accounts:
        print("No accounts to process.")
        return

    site_name = "Rollino"
    site_accounts = accounts.get(site_name, {})

    golden_data = load_golden_data(GOLDEN_JSON_FILE)

    new_project, changes_per_country = ro_refresh_methods(
        site_name,
        site_accounts,
        golden_data,
        run_func=run_playwright, 
        headless=headless
    )

    ro_log_changes(changes_per_country, RO_LOG_FILE)
    update_golden_file(golden_data, new_project, site_name)
    save_golden_data(golden_data, GOLDEN_JSON_FILE)

    print(f"Done. Golden ref: {GOLDEN_JSON_FILE.name}, log: {RO_LOG_FILE.name}")


if __name__ == "__main__":
    main(headless=True)
