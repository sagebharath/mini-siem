from fastapi import FastAPI, Request, Query
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import SessionLocal, engine
from app.models import Base, Event, Alert

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mini SIEM")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/")
def dashboard(request: Request):
    db = SessionLocal()

    event_count = db.query(Event).count()
    alert_count = db.query(Alert).count()
    recent_alerts = db.query(Alert).order_by(Alert.created_at.desc()).limit(10).all()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "event_count": event_count,
            "alert_count": alert_count,
            "recent_alerts": recent_alerts
        }
    )


@app.get("/events")
def events_page(
    request: Request,
    event_type: str = Query(default=""),
    source_ip: str = Query(default=""),
    username: str = Query(default="")
):
    db = SessionLocal()

    query = db.query(Event)

    if event_type:
        query = query.filter(Event.event_type.ilike(f"%{event_type}%"))

    if source_ip:
        query = query.filter(Event.source_ip.ilike(f"%{source_ip}%"))

    if username:
        query = query.filter(Event.username.ilike(f"%{username}%"))

    events = query.order_by(Event.timestamp.desc()).all()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="events.html",
        context={
            "events": events,
            "filters": {
                "event_type": event_type,
                "source_ip": source_ip,
                "username": username
            }
        }
    )


@app.get("/alerts")
def alerts_page(
    request: Request,
    severity: str = Query(default=""),
    source_ip: str = Query(default=""),
    status: str = Query(default="")
):
    db = SessionLocal()

    query = db.query(Alert)

    if severity:
        query = query.filter(Alert.severity.ilike(f"%{severity}%"))

    if source_ip:
        query = query.filter(Alert.source_ip.ilike(f"%{source_ip}%"))

    if status:
        query = query.filter(Alert.status.ilike(f"%{status}%"))

    alerts = query.order_by(Alert.created_at.desc()).all()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="alerts.html",
        context={
            "alerts": alerts,
            "filters": {
                "severity": severity,
                "source_ip": source_ip,
                "status": status
            }
        }
    )