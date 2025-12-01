import json
from playwright.sync_api import sync_playwright
from datetime import datetime
from data.config import *
import random

# === Common Utilities ===

def load_accounts():
    if not ACCOUNTS_FILE.exists():
        print(f"Accounts file {ACCOUNTS_FILE} not found!")
        return {}
    with ACCOUNTS_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)

def load_golden_data(golden_file):
    if golden_file.exists():
        with golden_file.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {"projects": []}

def save_golden_data(golden_data, golden_file):
    with golden_file.open("w", encoding="utf-8") as f:
        json.dump(golden_data, f, indent=2, ensure_ascii=False)

def update_golden_file(golden_data, new_project, site_name):
    project_found = False

    for proj in golden_data.get("projects", []):
        if proj.get("project") == site_name:
            project_found = True
            existing_countries = {c["country"]: c for c in proj.get("countries", [])}
            for new_country in new_project["countries"]:
                existing_countries[new_country["country"]] = new_country

            proj["countries"] = list(existing_countries.values())
            break

    if not project_found:
        golden_data.setdefault("projects", []).append(new_project)

def compare_methods(old_methods, new_methods):
    old_ids = {m["html_anchor"]: m for m in old_methods}
    new_ids = {m["html_anchor"]: m for m in new_methods}

    added = [m for anchor, m in new_ids.items() if anchor not in old_ids]
    removed = [m for anchor, m in old_ids.items() if anchor not in new_ids]

    return added, removed

def launch_browser(headless=True):
    LOCALES = ["en-US", "de-DE", "sv-SE", "it-IT", "en-GB"]
    TIMEZONES = ["Europe/Berlin", "Europe/Stockholm", "Europe/Rome", "Europe/London"]
    VIEWPORTS = [(1280, 800), (1366, 768), (1440, 900), (1536, 864)]
    locale = random.choice(LOCALES)
    timezone = random.choice(TIMEZONES)
    width, height = random.choice(VIEWPORTS)
    p = sync_playwright().start()
    browser = p.chromium.launch(
        channel="chrome",
        headless=headless,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-features=IsolateOrigins,site-per-process",
        ]
    )
    context = browser.new_context(
        viewport={"width": width, "height": height},
        locale=locale,
        timezone_id=timezone,
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/118.0.5993.70 Safari/537.36"
        ),
        permissions=["geolocation"],
        storage_state=None
    )
    page = context.new_page()
    
    # human touch
    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        window.navigator.chrome = { runtime: {} };
        Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
        Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
    """)
    
    return page, browser, p

# === PalmSlots Utilities ===

def ps_log_changes(changes_per_country):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [f"\n=== Date of checking: {now} ===\n"]
    for country in sorted(changes_per_country.keys()):
        changes = changes_per_country[country]
        lines.append(f"Country: {country}")
        if changes["added"]:
            lines.append("  Added:")
            for m in changes["added"]:
                lines.append(f"    + {m['payment_method']} ({m['html_anchor']})")
        if changes["removed"]:
            lines.append("  Removed:")
            for m in changes["removed"]:
                lines.append(f"    - {m['payment_method']} ({m['html_anchor']})")
        if not changes["added"] and not changes["removed"]:
            lines.append("  No changes.")
        lines.append("-" * 40)
    lines.append("")

    old_log = PS_LOG_FILE.read_text(encoding="utf-8") if PS_LOG_FILE.exists() else ""
    PS_LOG_FILE.write_text("\n".join(lines) + "\n" + old_log, encoding="utf-8")

def ps_fetch_methods(page):
    page.locator(PS_METHOD_SELECTOR).wait_for(state="visible", timeout=15000)
    methods = page.locator(PS_LIST_OF_METHODS_SELECTOR)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    result = []
    for i in range(methods.count()):
        el = methods.nth(i)
        testid = el.get_attribute("data-testid") or ""
        name = el.locator("p.MuiTypography-body1").first.text_content().strip()
        result.append({
            "payment_method": name,
            "html_anchor": testid,
            "timestamp": now
        })
    return result

def ps_get_country_methods(golden_data, project_name, country_name):
    """Returns list of payment_methods for given country"""
    for project in golden_data.get("projects", []):
        if project.get("project") == project_name:
            for country in project.get("countries", []):
                if country.get("country") == country_name:
                    return country.get("payment_methods", [])
    return []

def ps_refresh_methods(site_name, site_accounts, golden_data, run_func, headless=True):
    new_project = {"project": site_name, "countries": []}
    changes_per_country = {}

    for country, creds in site_accounts.items():
        print(f"Checking {country}...")
        methods = run_func(creds["username"], creds["password"], headless=headless)

        old_methods = ps_get_country_methods(golden_data, site_name, country)
        added, removed = compare_methods(old_methods, methods)

        changes_per_country[country] = {"added": added, "removed": removed}
        new_project["countries"].append({
            "country": country,
            "payment_methods": methods
        })

        print(f"{country}: {len(methods)} methods, added {len(added)}, removed {len(removed)}")

    return new_project, changes_per_country

# === Rollino/JettBet/CasinoJoy Utilities ===

def ro_log_changes(changes_per_country, log_file):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [f"\n=== Date of checking: {now} ===\n"]

    for country in sorted(changes_per_country.keys()):
        changes = changes_per_country[country]
        lines.append(f"Country: {country}")

        # Payment section
        lines.append("  Deposit Methods:")
        added = changes["payment_methods"]["added"]
        removed = changes["payment_methods"]["removed"]

        if added:
            lines.append("    Added:")
            for m in added:
                lines.append(f"      + {m['payment_method']} ({m['html_anchor']})")
        if removed:
            lines.append("    Removed:")
            for m in removed:
                lines.append(f"      - {m['payment_method']} ({m['html_anchor']})")
        if not added and not removed:
            lines.append("    No changes.")

        # Withdrawal section
        lines.append("  Withdrawal Methods:")
        added = changes["withdraw_methods"]["added"]
        removed = changes["withdraw_methods"]["removed"]

        if added:
            lines.append("    Added:")
            for m in added:
                lines.append(f"      + {m['withdraw_method']} ({m['html_anchor']})")
        if removed:
            lines.append("    Removed:")
            for m in removed:
                lines.append(f"      - {m['withdraw_method']} ({m['html_anchor']})")
        if not added and not removed:
            lines.append("    No changes.")

        lines.append("-" * 40)

    lines.append("")

    old_log = log_file.read_text(encoding="utf-8") if log_file.exists() else ""
    log_file.write_text("\n".join(lines) + "\n" + old_log, encoding="utf-8")

def ro_fetch_methods(page, list_of_methods_selector, method_type="payment"):
    methods = page.locator(list_of_methods_selector)
    result = []
    for i in range(methods.count()):
        el = methods.nth(i).locator("img")
        name = el.get_attribute("alt") or f"{method_type}_{i}"
        testid = el.get_attribute("src") or name
        if method_type == "payment":
            result.append({
                "payment_method": name,
                "html_anchor": testid,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        else:
            result.append({
                "withdraw_method": name,
                "html_anchor": testid,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
    return result

def ro_refresh_methods(site_name, site_accounts, golden_data, run_func, headless=True):
    new_project = {"project": site_name, "countries": []}
    changes_per_country = {}

    for country, creds in site_accounts.items():
        print(f"Checking {country}...")
        payment_methods, withdraw_methods = run_func(creds["username"], creds["password"], headless=headless)

        # old methods
        old_payment, old_withdraw = [], []
        for proj in golden_data.get("projects", []):
            if proj["project"] == site_name:
                for c in proj.get("countries", []):
                    if c["country"] == country:
                        old_payment = c.get("payment_methods", [])
                        old_withdraw = c.get("withdraw_methods", [])
                        break

        added_payment, removed_payment = compare_methods(old_payment, payment_methods)
        added_withdraw, removed_withdraw = compare_methods(old_withdraw, withdraw_methods)

        changes_per_country[country] = {
            "payment_methods": {"added": added_payment, "removed": removed_payment},
            "withdraw_methods": {"added": added_withdraw, "removed": removed_withdraw}
        }

        new_project["countries"].append({
            "country": country,
            "payment_methods": payment_methods,
            "withdraw_methods": withdraw_methods
        })

        print(
            f"{country}: payment {len(payment_methods)} methods, added {len(added_payment)}, removed {len(removed_payment)}, "
            f"withdraw {len(withdraw_methods)} methods, added {len(added_withdraw)}, removed {len(removed_withdraw)}"
        )
    return new_project, changes_per_country