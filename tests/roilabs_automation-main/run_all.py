import importlib
import sys
from data.config import HEADLESS
import shutil
from datetime import datetime

PROJECTS = {
    "jb": "tests.JB_payment_withdraw_methods",
    "ps": "tests.PS_payment_methods",
    "ro": "tests.RO_payment_withdraw_methods",
    "cj": "tests.CJ_payment_withdraw_methods",
}

def run_project(name, headless=True):
    module_name = PROJECTS.get(name.lower())
    if not module_name:
        print(f"❌ Unknown project: {name}")
        return
    print(f"\n=== Running {name} ===")
    module = importlib.import_module(module_name)
    module.main(headless=headless)

def run_all_projects(project_names, headless=True):
    for name in project_names:
        if name.lower() == "all":
            for p in PROJECTS:
                run_project(p, headless=headless)
        else:
            run_project(name, headless=headless)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        project_names = sys.argv[1:]
        run_all_projects(project_names, headless=HEADLESS)
    else:
        print("Usage:")
        print("  python run_all.py all                 # run all projects")
        print("  python run_all.py ps ro               # run exact project or multiple projects")

    shutil.copy("current_methods.json", f"current_methods_{datetime.today().strftime("%Y_%m_%d")}.json")
    print("Copied current_methods.json to a dated backup created in" + f"current_methods_{datetime.today().strftime("%Y_%m_%d")}.json")
