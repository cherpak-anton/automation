# tests/wikly/source/main.py
from playwright.sync_api import sync_playwright

def test_homepage_status():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        response = page.goto("https://example.com")
        assert response.status == 200
        
        browser.close()