from app.database import SessionLocal
from app.detection.engine import run_detection

def main():
    db = SessionLocal()
    run_detection(db)
    db.close()
    print("Detection completed successfully.")

if __name__ == "__main__":
    main()