import hashlib
import json

from app.database import SessionLocal, engine
from app.models import Base, Event
from app.parser.windows_event_parser import parse_windows_event_log

Base.metadata.create_all(bind=engine)

LOG_FILE = "logs/windows_events.log"


def event_exists(db, parsed_event):
    existing_event = db.query(Event).filter(
        Event.timestamp == parsed_event["timestamp"],
        Event.event_id == parsed_event["event_id"],
        Event.source_ip == parsed_event["source_ip"],
        Event.username == parsed_event["username"],
        Event.raw_log == parsed_event["raw_log"]
    ).first()

    return existing_event is not None


def compute_event_hash(parsed_event, previous_hash=""):
    hash_input = json.dumps(
        {
            "timestamp": parsed_event["timestamp"].isoformat() if parsed_event["timestamp"] else "",
            "event_id": parsed_event["event_id"],
            "source": parsed_event["source"],
            "event_type": parsed_event["event_type"],
            "username": parsed_event["username"],
            "source_ip": parsed_event["source_ip"],
            "host": parsed_event["host"],
            "service": parsed_event["service"],
            "status": parsed_event["status"],
            "raw_log": parsed_event["raw_log"],
            "previous_hash": previous_hash
        },
        sort_keys=True
    )

    return hashlib.sha256(hash_input.encode()).hexdigest()


def ingest():
    db = SessionLocal()
    inserted_count = 0
    skipped_count = 0

    last_event = db.query(Event).order_by(Event.id.desc()).first()
    previous_hash = last_event.log_hash if last_event and last_event.log_hash else ""

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            parsed = parse_windows_event_log(line)

            if parsed:
                if event_exists(db, parsed):
                    skipped_count += 1
                    continue

                log_hash = compute_event_hash(parsed, previous_hash)

                parsed["previous_hash"] = previous_hash
                parsed["log_hash"] = log_hash

                event = Event(**parsed)
                db.add(event)

                previous_hash = log_hash
                inserted_count += 1

    db.commit()
    db.close()

    print(f"Logs ingested successfully. Inserted: {inserted_count}, Skipped duplicates: {skipped_count}")


if __name__ == "__main__":
    ingest()