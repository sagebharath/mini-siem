from app.database import SessionLocal
from app.models import Alert

db = SessionLocal()

alerts = db.query(Alert).all()

print(f"Total alerts in DB: {len(alerts)}")
print("-" * 50)

for alert in alerts:
    print(
        f"ID={alert.id}, "
        f"rule={alert.rule_name}, "
        f"severity={alert.severity}, "
        f"source_ip={alert.source_ip}, "
        f"event_count={alert.event_count}, "
        f"status={alert.status}, "
        f"description={alert.description}"
    )

db.close()