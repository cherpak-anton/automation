# file: infra/proxy_lambda/source/main.py

from runner.log_manager import log, get_logs
from runner.executor import run_python_project
import tempfile, shutil, json, traceback
import os 
import sys 
import base64

def get_run_params():
    try:
        job_data_b64 = os.environ.get('INPUT_PAYLOAD') 
        
        if not job_data_b64:
            data = {} 
            log("No INPUT_PAYLOAD found, proceeding with empty data.")
        else:
            job_data_decoded = base64.b64decode(job_data_b64).decode('utf-8')
            
            data = json.loads(job_data_decoded)
            log(f"Received INPUT_PAYLOAD: {json.dumps(data)}")

    except (json.JSONDecodeError, base64.binascii.Error) as e:
        log(f"Error: Failed to decode/parse INPUT_PAYLOAD: {e}")
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