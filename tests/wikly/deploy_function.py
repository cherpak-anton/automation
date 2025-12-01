import subprocess
import datetime
import base64
import json
import time
import sys
import re

REGIONS = ["us-central1"]
FUNCTION = "my-function"

def log_analizer(logs):
    exit_code_pattern = re.compile(r'exit_?code[:\s]+(\d+)', re.IGNORECASE)
    print(f"Найдено {len(logs)} записей логов.")
    job_failed = False

    for entry in logs:
        payload = entry.get('textPayload') or entry.get('jsonPayload')
        print(f"[{entry.get('timestamp')}] {payload}")

        if isinstance(payload, str):
            match = exit_code_pattern.search(payload)
            if match:
                exit_code = int(match.group(1))
                if exit_code != 0:
                    job_failed = True
                    print(f"🚨 Найдено regex: ненулевой код выхода {exit_code}")

            if "FAILED" in payload:
                job_failed = True
                
        elif isinstance(payload, dict):
            exit_code = payload.get("exit_code")
            if exit_code is not None and exit_code != 0:
                job_failed = True
                print(f"🚨 Найдено JSON: ненулевой код выхода {exit_code}") 
                
    if job_failed:
        print("\n🚨 ОБНАРУЖЕН СБОЙ ВЫПОЛНЕНИЯ! Сборка будет прервана.")
        raise Exception("Выполнение Job Cloud Run завершилось с ошибкой. См. логи выше.")
        
    return "SUCCESS"
    
    


def get_execution_logs(response_json_str, region, project_id):       
    try: 
        response_json = json.loads(response_json_str)
        execution_name = response_json.get('metadata', {}).get('name')
    except Exception as e:
        print("error", e)

    if not execution_name:
        # Это может случиться, если Job завершился слишком быстро или упал при старте
        raise Exception("Не удалось получить Execution ID из ответа Cloud Run. Проверьте системные логи.")
    
    log_filter = (
        f'resource.type="cloud_run_job" AND "{execution_name}"'
    )

    log_read_command = [
        'gcloud', 'logging', 'read', log_filter,
        '--project', project_id,
        '--order=asc',
        '--format=json' 
    ]

    time.sleep(10)
    log_result = subprocess.run(log_read_command, check=False, capture_output=True, text=True)
    
    if log_result.stdout:
        logs = json.loads(log_result.stdout)
        if logs:
            return log_analizer(logs)

    raise Exception("Не удалось получить логи Job'а. Сборка прервана.")

def execute_command(command, region, project_id):
    try:
        # Run command
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("Finished", datetime.datetime.now())
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