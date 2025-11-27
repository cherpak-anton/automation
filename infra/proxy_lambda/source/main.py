# file: runner/main.py

from runner.executor import run_python_tests
from runner.logger import Logger

log = Logger().log
get_logs = Logger().get 


def main(params=None):

    if params is None:
        params = {
            "region": "US",
            "locale": "en-US",
            "branch": "main",
            "repo_url": "https://github.com/your-org/your-tests.git"
        }

    try:
        log(f"Params received: {params}")

        # replace real run:
        output = params

        log("Execution finished.")
        log(f"Output: {output}")

        return {
            "logs": get_logs(),
            "result": output
        }

    except Exception as e:
        log(f"ERROR: {e}")
        return {
            "logs": get_logs(),
            "error": str(e)
        }
