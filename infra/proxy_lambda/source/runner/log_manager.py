# file: runner/logger.py

import datetime

class Logger:
    def __init__(self, logfile="/tmp/log.txt"):
        self.logfile = logfile
        self.buffer = []

    def log(self, text: str):
        """Write to file, store in memory, print."""
        # timestamp = datetime.datetime.utcnow().isoformat()
        # line = f"[{timestamp}] {text}"

        # self.buffer.append(line)
        self.buffer.append(text)

        with open(self.logfile, "a") as f:
            f.write(line + "\n")

        print(line)

    def get_logs(self):
        """Return all collected logs."""
        return self.buffer[:]

# GLOBAL singleton
logger = Logger()
log = logger.log
get_logs = logger.get_logs