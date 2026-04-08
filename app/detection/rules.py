from datetime import timedelta
from app.models import Event, Alert


def alert_exists(db, rule_name, source_ip, first_seen, last_seen):
    existing_alert = db.query(Alert).filter(
        Alert.rule_name == rule_name,
        Alert.source_ip == source_ip,
        Alert.first_seen == first_seen,
        Alert.last_seen == last_seen
    ).first()

    return existing_alert is not None


def detect_brute_force(db):
    failed_events = db.query(Event).filter(Event.event_type == "login_failed").all()

    ip_event_map = {}

    for event in failed_events:
        if not event.source_ip:
            continue

        if event.source_ip not in ip_event_map:
            ip_event_map[event.source_ip] = []

        ip_event_map[event.source_ip].append(event)

    for ip, events in ip_event_map.items():
        events = sorted(events, key=lambda x: x.timestamp)

        if len(events) >= 5:
            first_seen = events[0].timestamp
            last_seen = events[-1].timestamp

            if last_seen - first_seen <= timedelta(minutes=5):
                if alert_exists(db, "Brute Force Detection", ip, first_seen, last_seen):
                    continue

                alert = Alert(
                    rule_name="Brute Force Detection",
                    severity="high",
                    description=f"Detected {len(events)} failed logins from IP {ip} within 5 minutes.",
                    source_ip=ip,
                    event_count=len(events),
                    first_seen=first_seen,
                    last_seen=last_seen,
                    status="open"
                )
                db.add(alert)


def detect_success_after_failures(db):
    all_ips = db.query(Event.source_ip).distinct().all()
    all_ips = [ip[0] for ip in all_ips if ip[0]]

    for ip in all_ips:
        events = db.query(Event).filter(Event.source_ip == ip).order_by(Event.timestamp).all()

        failed_count = 0
        first_failure_time = None

        for event in events:
            if event.event_type == "login_failed":
                failed_count += 1
                if first_failure_time is None:
                    first_failure_time = event.timestamp

            elif event.event_type == "login_success" and failed_count >= 3:
                if alert_exists(db, "Success After Failures", ip, first_failure_time, event.timestamp):
                    break

                alert = Alert(
                    rule_name="Success After Failures",
                    severity="medium",
                    description=f"IP {ip} had {failed_count} failed logins followed by a successful login.",
                    source_ip=ip,
                    event_count=failed_count + 1,
                    first_seen=first_failure_time,
                    last_seen=event.timestamp,
                    status="open"
                )
                db.add(alert)
                break