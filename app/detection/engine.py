from app.detection.rules import detect_brute_force, detect_success_after_failures

def run_detection(db):
    detect_brute_force(db)
    detect_success_after_failures(db)
    db.commit()
    