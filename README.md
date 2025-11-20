project/
│
├── main.py                # главная Cloud Function
├── runner/
│   ├── executor.py        # загрузка + исполнение кода
│   ├── storage.py         # работа с Cloud Storage
│   ├── logger.py          # логгер
│
├── requirements.txt
└── README.md



#################################################################################################################################
Этот файл:

создаёт Pub/Sub-топик, если его нет
деплоит функцию в каждый регион
создаёт Cloud Scheduler weekly-job, если его нет
job → Pub/Sub → функция раз в неделю
Ничего руками больше подключать не надо.

steps:
  - name: "gcr.io/google.com/cloudsdktool/cloud-sdk:latest"
    entrypoint: "python3"
    args:
      - "-c"
      - |
        import subprocess, json

        PROJECT = subprocess.check_output(
            ["gcloud", "config", "get-value", "project"], text=True
        ).strip()

        REGIONS = ["us-central1"]
        FUNCTION_NAME = "my_function"
        RUNTIME = "python311"
        ENTRY_POINT = "main"
        TOPIC = "weekly-trigger"
        SCHEDULE = "0 0 * * 0"  # once per week (Sunday 00:00)

        # Create Pub/Sub topic if missing
        print("Creating Pub/Sub topic if not exists...")
        subprocess.run(
            ["gcloud", "pubsub", "topics", "create", TOPIC, "--quiet"],
            check=False
        )

        for region in REGIONS:
            print(f"Deploying function to region: {region}")

            # Deploy function with Pub/Sub trigger
            deploy_cmd = [
                "gcloud", "functions", "deploy", FUNCTION_NAME,
                "--gen2",
                f"--region={region}",
                f"--runtime={RUNTIME}",
                "--source=.",
                f"--entry-point={ENTRY_POINT}",
                f"--trigger-topic={TOPIC}",
                "--allow-unauthenticated"
            ]
            subprocess.run(deploy_cmd, check=True)

            print(f"Function deployed in {region}")

        # Create Cloud Scheduler job if missing
        print("Creating Cloud Scheduler weekly job if not exists...")

        subprocess.run(
            [
                "gcloud", "scheduler", "jobs", "create", "pubsub", "weekly-job",
                f"--schedule={SCHEDULE}",
                f"--topic={TOPIC}",
                "--message-body='run'",
                "--time-zone=UTC",
                "--quiet"
            ],
            check=False
        )

timeout: 1200s
options:
  logging: CLOUD_LOGGING_ONLY

##################################################################################################################################