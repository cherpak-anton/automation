from runner.executor import run_python_tests
from runner.logger import log

def main(region="US", locale="en-US", branch="main", repo_url="https://github.com/your-org/your-tests.git"):
    """
    Entry point for scheduled or Cloud Build-triggered execution.
    """
    log(f"Trigger received. Repo: {repo_url}, Branch: {branch}, Region: {region}, Locale: {locale}")

    try:
        output = run_python_tests(repo_url, branch, region, locale)
        log("Execution finished.")
        log(f"Output: {output}")
        return output
    except Exception as e:
        log(f"ERROR: {e}")
        return {"error": str(e)}
