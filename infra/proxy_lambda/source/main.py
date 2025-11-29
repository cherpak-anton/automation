# file: infra/proxy_lambda/source/main.py

import tempfile, shutil, json, traceback
from flask import Request
from runner.log_manager import log, get_logs
from runner.executor import run_python_project

def main(request: Request):
    try:
        log("Received request")  

        data = request.get_json(force=True)
        log(json.dumps(data))  # log full input

        result = run_python_project(data)

        log(f"stdout: {result.get('stdout')}")
        log(f"stderr: {result.get('stderr')}")
        log(f"exit_code: {result.get('exit_code')}")

        # Logs must be plain list/str for JSON
        logs = get_logs()
        if not isinstance(logs, (list, str)):
            logs = str(logs)

        # Determine HTTP status
        status_code = 200 if result.get("exit_code", 1) == 0 else 500

        return {
            "status": "ok",
            "request": data,
            "stdout": result.get("stdout"),
            "stderr": result.get("stderr"),
            "logs": logs
        }, status_code

    except Exception:
        log(f"Error: {traceback.format_exc()}")
        logs =get_logs()
        if not isinstance(logs, (list, str)):
            logs = str(logs)
        return {"status": "error", "message": "internal error", "logs": logs}, 500
