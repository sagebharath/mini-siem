import hashlib
import json

from app.database import SessionLocal
from app.models import Event


def compute_event_hash(event, previous_hash=""):
    hash_input = json.dumps(
        {
            "timestamp": event.timestamp.isoformat() if event.timestamp else "",
            "event_id": event.event_id,
            "source": event.source,
            "event_type": event.event_type,
            "username": event.username,
            "source_ip": event.source_ip,
            "host": event.host,
            "service": event.service,
            "status": event.status,
            "raw_log": event.raw_log,
            "previous_hash": previous_hash
        },
        sort_keys=True
    )

    return hashlib.sha256(hash_input.encode()).hexdigest()


def verify_integrity():
    db = SessionLocal()
    events = db.query(Event).order_by(Event.id.asc()).all()

    previous_hash = ""

    for event in events:
        expected_hash = compute_event_hash(event, previous_hash)

        if event.previous_hash != previous_hash:
            print(f"[FAIL] Event ID {event.id}: previous_hash mismatch")
            db.close()
            return

        if event.log_hash != expected_hash:
            print(f"[FAIL] Event ID {event.id}: log_hash mismatch")
            db.close()
            return

        previous_hash = event.log_hash

    db.close()
    print("[OK] Log integrity verified successfully.")


if __name__ == "__main__":
    verify_integrity()