# tests/wikly/source/test_main.py
from playwright.sync_api import sync_playwright
import os
import pytest
import base64
import json
from binascii import Error as BinasciiError

global DATA_PARAMS 
DATA_PARAMS = {}

def test_get_run_params():
    global DATA_PARAMS 
    
    try:
        job_data_b64 = os.environ.get('INPUT_PAYLOAD')
        assert job_data_b64 is not None and job_data_b64 != "", \
            "CRITICAL FAILURE: INPUT_PAYLOAD environment variable is missing or empty."

        job_data_decoded = base64.b64decode(job_data_b64).decode('utf-8')
        DATA_PARAMS = json.loads(job_data_decoded)

    except (BinasciiError, UnicodeDecodeError) as e:
        pytest.fail(f"CRITICAL ERROR: Failed to decode Base64/UTF-8 for INPUT_PAYLOAD. Data is corrupted. Error: {e}")
        
    except json.JSONDecodeError as e:
        pytest.fail(f"CRITICAL ERROR: Failed to parse JSON from INPUT_PAYLOAD. Data format is invalid. Error: {e}")

    print(f"Loaded parameters: {DATA_PARAMS}")
    assert isinstance(DATA_PARAMS, dict) and len(DATA_PARAMS) > 0, \
        "Parameters loaded successfully but are unexpectedly empty."


def test_homepage_status():
    print(DATA_PARAMS)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        response = page.goto("https://example.com")
        assert response.status == 200
        
        browser.close()