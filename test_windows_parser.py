from app.parser.windows_event_parser import parse_windows_event_log

LOG_FILE = "logs/windows_events.log"

with open(LOG_FILE, "r") as f:
    for line in f:
        parsed = parse_windows_event_log(line)
        print(parsed)