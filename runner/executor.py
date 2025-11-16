import subprocess
import zipfile
import os
from .storage import download_from_gcs
from .logger import log

CODE_ZIP = "/tmp/code.zip"
CODE_DIR = "/tmp/code"
ENTRY_FILE = "main.py"  # можно поменять


def run_python_code(gcs_url: str):

    # 1. Download
    log("Downloading code...")
    download_from_gcs(gcs_url, CODE_ZIP)

    # 2. Unzip
    if os.path.exists(CODE_DIR):
        subprocess.run(["rm", "-rf", CODE_DIR])
    os.makedirs(CODE_DIR, exist_ok=True)

    with zipfile.ZipFile(CODE_ZIP, 'r') as z:
        z.extractall(CODE_DIR)

    log("Code unzipped.")

    # 3. Execute
    entry_path = os.path.join(CODE_DIR, ENTRY_FILE)

    if not os.path.isfile(entry_path):
        raise FileNotFoundError(f"Entry file '{ENTRY_FILE}' not found in archive")

    log("Running Python entry file: " + entry_path)

    result = subprocess.run(
        ["python3", entry_path],
        capture_output=True,
        text=True
    )

    log("Execution stdout:\n" + result.stdout)
    log("Execution stderr:\n" + result.stderr)

    return result.stdout

