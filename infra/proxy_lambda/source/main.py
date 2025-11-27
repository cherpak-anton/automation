# file: infra/proxy_lambda/source/main.py

from functions_framework import create_app
from runner.executor import run_python_tests
from runner.logger import Logger
import traceback
import json

logger = Logger()
log = logger.log

def entrypoint(request):
    """
    Cloud Functions Gen2 HTTP entrypoint
    `request` — объект flask-like с методами .get_json(), .args, etc.
    """
    try:
        params = request.get_json(silent=True)
        if params is None:
            params = {
                "region": "US",
                "locale": "en-US",
                "branch": "main",
                "repo_url": "https://github.com/your-org/your-tests.git"
            }

        log(f"Params received: {params}")

        # --- реальный запуск ---
        output = params  # run_python_tests(...) заменяем на заглушку

        log("Execution finished.")
        log(f"Output: {output}")

        response = {
            "logs": logger.get_logs(),
            "result": output,
            "status": "ok"
        }
        return json.dumps(response), 200, {"Content-Type": "application/json"}

    except Exception as e:
        tb = traceback.format_exc()
        log(f"ERROR: {e}")
        log(tb)

        response = {
            "logs": logger.get_logs(),
            "error": str(e),
            "traceback": tb,
            "status": "Error"
        }
        return json.dumps(response), 500, {"Content-Type": "application/json"}


# Create HTTP app for GCF Gen2
app = create_app(target=entrypoint)