# file: infra/proxy_lambda/source/main.py

from runner.log_manager import log, get_logs
from runner.executor import run_python_project
import tempfile, shutil, json, traceback
import os 
import sys 

def get_run_params():
    try:
        job_data_json = os.environ.get('JOB_DATA')
        
        if not job_data_json:
            data = {} 
            log("No JOB_DATA found, proceeding with empty data.")
        else:
            data = json.loads(job_data_json)
            log(f"Received JOB_DATA: {json.dumps(data)}")

    except json.JSONDecodeError:
        log("Error: Failed to decode JOB_DATA JSON.")
        sys.exit(1)

    return data


def main():
    try:
        log("INFO: Cloud Run Job script starting.")
        log("Job started")

        data = get_run_params()
        log(json.dumps(data))

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


if __name__ == "__main__":
    main()
    log("INFO: Cloud Run Job script finished. Container shutting down.")