from datetime import datetime
from pathlib import Path

LOG = Path(__file__).parent.parent / "activity.log"

def record_activity(message):
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    with LOG.open("a", encoding="utf-8") as file:
        file.write(f"{timestamp} | {message}\n")
    print("Activity recorded.")

if __name__ == "__main__":
    message = input("What did you work on today? ").strip()
    if message:
        record_activity(message)
