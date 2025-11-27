# file: infra/proxy_lambda/surce/main.py

# from runner.executor import run_python_tests
# from runner.logger import Logger
# import traceback

# logger = Logger()
# log = logger.log

def main(params=None):
    return {"status": "ok"}, 200


# def main(params=None):
#     pass
    # if params is None:
    #     params = {
    #         "region": "US",
    #         "locale": "en-US",
    #         "branch": "main",
    #         "repo_url": "https://github.com/your-org/your-tests.git"
    #     }

    # try:
    #     log(f"Params received: {params}")

    #     # --- сюда вставляется реальный запуск ---
    #     output = params  # replace with: run_python_tests(...)

    #     log("Execution finished.")
    #     log(f"Output: {output}")

    #     return {
    #         "logs": logger.get_logs(),
    #         "result": output
    #     }

    # except Exception as e:
    #     tb = traceback.format_exc()
    #     log(f"ERROR: {e}")
    #     log(tb)
    #     return {
    #         "logs": logger.get_logs(),
    #         "error": str(e),
    #         "traceback": tb
    #     }
