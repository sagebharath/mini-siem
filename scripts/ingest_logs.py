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


def ingest():
    db = SessionLocal()
    inserted_count = 0
    skipped_count = 0

    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            parsed = parse_windows_event_log(line)

            if parsed:
                if event_exists(db, parsed):
                    skipped_count += 1
                    continue

                event = Event(**parsed)
                db.add(event)
                inserted_count += 1

    db.commit()
    db.close()

    print(f"Logs ingested successfully. Inserted: {inserted_count}, Skipped duplicates: {skipped_count}")


if __name__ == "__main__":
    ingest()