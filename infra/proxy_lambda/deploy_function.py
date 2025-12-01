# infra/proxy_lambda/deploy_function.py
import subprocess
import json
import os
import sys

REGIONS = ["us-central1", "europe-west2"]        
FUNCTION_NAME = "my-function"
ENTRY_POINT = "main"

def deploy_functions():
    try:
        project_id = os.environ['PROJECT_ID']
    except KeyError:
        print("Error: PROJECT_ID environment variable not set.")
        sys.exit(1)

    docker_image = f"gcr.io/{project_id}/{FUNCTION_NAME}:latest"

    deployed = []

    for region in REGIONS:
        print(f"Deploying function to region: {region}")

        check_cmd = [
            'gcloud', 'run', 'jobs', 'describe', FUNCTION_NAME,
            f'--region={region}',
            '--format=disable',
        ]
        check_result = subprocess.run(check_cmd, check=False, capture_output=True)

        if check_result.returncode == 0:
            operation = 'update'
            print(f"Job {FUNCTION_NAME} существует. Обновляем...")
        else:
            operation = 'deploy'
            print(f"Job {FUNCTION_NAME} не найден. Создаем (deploy)...")
        
        command = [
            'gcloud', 'run', 'jobs', operation, FUNCTION_NAME,
            f'--region={region}',
            f'--image={docker_image}',
            '--task-timeout', '1800s',
            '--command', 'python',
            '--args', 'main.py'
        ]
        
        subprocess.run(command, check=True)
        describe_cmd = [
            'gcloud', 'run', 'jobs', 'describe', FUNCTION_NAME,
            f'--region={region}',
            '--format=json'
        ]
        result = subprocess.run(describe_cmd, check=True, capture_output=True, text=True)
        func_info = json.loads(result.stdout)
        deployed.append(func_info)
        print(f"Successfully deployed to {region}")

    with open('/workspace/functions.json', 'w') as f:
        json.dump(deployed, f)

if __name__ == "__main__":
    deploy_functions()