from utils.utils import (load_accounts,
                         load_golden_data,
                         save_golden_data,
                         ps_log_changes,
                         launch_browser,
                         ps_fetch_methods,
                         ps_refresh_methods,
                         update_golden_file)
from data.config import *

def run_playwright(username, password, headless=True):
    page, browser, p = launch_browser(headless=headless)

    page.goto(PS_URL, timeout=90000)

    # login
    page.wait_for_selector(PS_LOGIN_BUTTON, timeout=60000)
    page.locator(PS_LOGIN_BUTTON).click()
    page.locator(PS_USERNAME_FIELD).fill(username)
    page.locator(PS_PASSWORD_FIELD).fill(password)
    page.locator(PS_SUBMIT_BUTTON).click()

    # open deposit modal
    page.locator(PS_DEPOSIT_BUTTON_SELECTOR).first.click()
    page.wait_for_selector(PS_CASHIER_MODAL_SELECTOR, state="visible", timeout=60000)
    page.wait_for_selector(PS_CASHIER_IFRAME_SELECTOR, timeout=60000)
    frame = page.frame_locator(PS_CASHIER_IFRAME_SELECTOR)

    methods = ps_fetch_methods(frame)
    browser.close()
    p.stop()
    return methods

def main(headless=True):
    accounts = load_accounts()
    if not accounts:
        print("No accounts to process.")
        return

    site_name = "Palmslots"
    site_accounts = accounts.get(site_name, {})
    if not site_accounts:
        print(f"No site accounts found for {site_name}.")
        return
    
    golden_data = load_golden_data(GOLDEN_JSON_FILE)
        
    new_project, changes_per_country = ps_refresh_methods(
        site_name,
        site_accounts,
        golden_data,
        run_func=run_playwright, 
        headless=headless
    )

    ps_log_changes(changes_per_country)
    update_golden_file(golden_data, new_project, site_name)
    save_golden_data(golden_data, GOLDEN_JSON_FILE)

    print(f"Done. Golden ref: {GOLDEN_JSON_FILE.name}, log: {PS_LOG_FILE.name}")


if __name__ == "__main__":
    main(headless=True)
