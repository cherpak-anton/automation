# filename: infra/proxy_lambda/source/runner/executor.py

import os
import subprocess
import tempfile
from runner.log_manager import log
from runner.storage import download_dir_from_gcs


def download_project(data):
    """Download project from GCS into temp folder and return path."""
    tmp = tempfile.mkdtemp()
    log(f"tmp: {tmp}")

    try:
        download_dir_from_gcs(data["source"], tmp)
    except Exception as e:
        log(f"Download error: {str(e)}")
        raise

    return tmp

def run_python_project(data):
    """Download project, install requirements, run main.py, return stdout/stderr/exit_code."""
    # Step 1: download project
    path = download_project(data)
    log(f"Project downloaded to {path}")

    req = os.path.join(path, "requirements.txt")
    main_py = os.path.join(path, "main.py")
    init_sh = os.path.join(path, "init.sh") 

    # English comment: install dependencies if present
    # Step 2: install requirements
    if os.path.exists(req):
        log("installing requirements.txt")
        req_proc = subprocess.run(
            ["pip3", "install", "-r", req, "--target", path],
            capture_output=True,
            text=True
        )
        log(f"pip exit_code: {req_proc.returncode}")
        log(f"pip stdout: {req_proc.stdout}")
        log(f"pip stderr: {req_proc.stderr}")

    # Step 3: determine entrypoint
    if os.path.exists(init_sh):
        log("found init.sh, giving it priority over main.py")
        entry_cmd = ["bash", init_sh]
    elif os.path.exists(main_py):
        entry_cmd = ["python3", main_py]
    else:
        raise Exception("Neither main.py nor init.sh found in downloaded project")

    # Step 4: run entrypoint
    log(f"executing {'init.sh' if os.path.exists(init_sh) else 'main.py'}")
    proc = subprocess.run(
        entry_cmd,
        cwd=path,
        capture_output=True,
        text=True
    )
    log("execution finished")

    # Step 5: cleanup
    subprocess.run(["rm", "-rf", path])

    return {
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "exit_code": proc.returncode
    }
