import json
from flask import Request
from runner.executor import run_python_code
from runner.logger import log

def main(request: Request):

    try:
        payload = request.get_json(silent=True)

        if not payload:
            return {"error": "Empty request"}, 400

        code_url = payload.get("code_url")

        if not code_url:
            return {"error": "code_url is required"}, 400

        log("Trigger received. Code URL: " + code_url)

        # run code
        output = run_python_code(code_url)

        log("Execution finished.")
        log("Output: " + str(output))

        return {"status": "ok", "output": output}, 200

    except Exception as e:
        log("ERROR: " + str(e))
        return {"error": str(e)}, 500

