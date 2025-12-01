import subprocess
import base64
import json
import time
import sys

REGIONS = ["us-central1"]
FUNCTION = "my-function"

def get_execution_logs(response_json_str, region, project_id):       
    try: 
        response_json = json.loads(response_json_str)
        execution_name = response_json.get('metadata', {}).get('name')
    except Exception as e:
        print("error", e)

    if not execution_name:
        # Это может случиться, если Job завершился слишком быстро или упал при старте
        raise Exception("Не удалось получить Execution ID из ответа Cloud Run. Проверьте системные логи.")
    
    print(f"Execution ID: {execution_name}")

    # Фильтр для gcloud logging read
    log_filter = (
        f'resource.type="cloud_run_revision" '
        f'resource.labels.service_name="{FUNCTION}" '
        f'resource.labels.location="{region}" '
        f'(labels."run.googleapis.com/job_execution_id"="{execution_name}" '
        f'OR labels."run.googleapis.com/execution_id"="{execution_name}")'
    )

    log_read_command = [
        'gcloud', 'logging', 'read', log_filter,
        '--project', project_id,
        "--limit=1000",
        '--format=json' 
    ]
    time.sleep(15)

    log_result = subprocess.run(log_read_command, check=False, capture_output=True, text=True)
    print("log_result", log_result)
    
    # Выводим найденные логи
    if log_result.stdout:
        logs = json.loads(log_result.stdout)
        if logs:
            print(f"Найдено {len(logs)} записей логов.")
            for entry in logs:
                # Выводим текст сообщения или JSON-тело
                payload = entry.get('textPayload') or entry.get('jsonPayload')
                print(f"[{entry.get('timestamp')}] {payload}")
        else:
            print("Логи не найдены в Cloud Logging для этого Execution ID.")
    else:
        print("Ошибка при чтении логов Gcloud (проверьте права доступа).")
    
    return "SUCCESS" # Возвращаем признак успеха


def execute_command(command, region, project_id):
    try:
        # Run command
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        response_json_str = result.stdout.strip()
        print("response_json_str", response_json_str)

        if not response_json_str:
            print("response_json_str пуст. Проверьте, что команда завершилась успешно и вернула JSON.")
            # Если команда завершилась успешно, но stdout пуст, проверим stderr на системные сообщения
            if result.stderr:
                print("Системный вывод (stderr):", result.stderr.strip())
            raise Exception("Пустой ответ от gcloud run jobs execute. Не удалось получить Execution ID.")

        return get_execution_logs(response_json_str, region, project_id)

    except subprocess.CalledProcessError as e:
        # Критическая ошибка gcloud (например, неверный синтаксис или Job не существует)
        print("\n❌ Critical error")
        print(f"Command: {' '.join(e.cmd)}")
        print(f"Stderr: {e.stderr.strip()[:500]}")
        sys.exit(1)

    except Exception as e:
        # Ошибка парсинга JSON или другая ошибка
        print(f"\n❌ Execution/Parsing Error: {e}")
        sys.exit(1)

def main(build_id, project_id):
    for region in REGIONS:
        print(f"\n--- Начинаем вызов Cloud Run Job {FUNCTION} в регионе {region} ---")

        payload = str(json.dumps({
            'source': 'gs://qa-test-roidev/tests-wikly/source/',
            'region': region,
            'build_id': build_id
        }))
        b64_str = base64.b64encode(payload.encode('utf-8')).decode('utf-8')
        payload_value = f"INPUT_PAYLOAD='{b64_str}'"

        job_execute_command = [
            'gcloud', 'run', 'jobs', 'execute', FUNCTION,
            f'--region={region}',
            f'--update-env-vars={payload_value}',
            '--format=json',
            '--wait'
        ]

        print(f"Вызываем Job. Команда: {' '.join(job_execute_command)}")
        execute_command(job_execute_command, region, project_id)
        print(f"✅ Успешно вызвано {FUNCTION} в {region}. Результат в логах Cloud Logging.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python invoke_job.py <BUILD_ID> <PROJECT_ID>")
        sys.exit(1)

    build_id = sys.argv[1]
    project_id = sys.argv[2]

    main(build_id, project_id)