# filename: runner/executor.py

import os
import subprocess
import tempfile
from runner.logger import log

def run_python_tests(repo_url: str, branch: str = "main", region: str = "US", locale: str = "en-US"):
    """
    Clone tests from Git, install test dependencies, and run Playwright tests.
    Returns dict with stdout, stderr, returncode.
    """
    log(f"Starting test execution. Repo: {repo_url}, Branch: {branch}, Region: {region}, Locale: {locale}")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Clone repo
        log("Cloning repository...")
        subprocess.run(["git", "clone", repo_url, tmpdir], check=True)
        subprocess.run(["git", "checkout", branch], cwd=tmpdir, check=True)

        # Install additional test dependencies if requirements-tests.txt exists
        req_file = os.path.join(tmpdir, "requirements-tests.txt")
        if os.path.exists(req_file):
            log("Installing additional test dependencies...")
            subprocess.run(["pip", "install", "-r", req_file], check=True)

        # Ensure Playwright browsers installed
        log("Installing Playwright browsers...")
        subprocess.run(["playwright", "install"], check=True)

        # Set environment variables for tests
        env = os.environ.copy()
        env["REGION"] = region
        env["LOCALE"] = locale

        # Run pytest on tests folder
        log("Running tests...")
        result = subprocess.run(
            ["pytest", "tests", "--maxfail=5", "--disable-warnings", "-q"],
            cwd=tmpdir,
            env=env,
            capture_output=True,
            text=True
        )

        log("Test execution finished.")
        log(f"Return code: {result.returncode}")

        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
