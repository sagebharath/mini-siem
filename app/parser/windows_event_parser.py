import json
from datetime import datetime


def parse_windows_event_log(line: str):
    line = line.strip()

    if not line:
        return None

    try:
        data = json.loads(line)
    except json.JSONDecodeError:
        return None

    try:
        timestamp = datetime.fromisoformat(data["timestamp"])
    except (KeyError, ValueError):
        return None

    return {
        "timestamp": timestamp,
        "event_id": data.get("event_id"),
        "source": "windows_security",
        "event_type": data.get("event_type"),
        "username": data.get("username"),
        "source_ip": data.get("source_ip"),
        "host": data.get("host"),
        "service": data.get("service", "windows_security"),
        "status": data.get("status"),
        "raw_log": data.get("raw_log", line)
    }