import datetime

LOGFILE = "/tmp/log.txt"

def log(text: str):
    timestamp = datetime.datetime.utcnow().isoformat()
    
    with open(LOGFILE, "a") as f:
        f.write(f"[{timestamp}] {text}\n")

