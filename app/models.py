from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from app.database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=True)
    event_id = Column(Integer, nullable=True)
    source = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    username = Column(String, nullable=True)
    source_ip = Column(String, nullable=True)
    host = Column(String, nullable=True)
    service = Column(String, nullable=True)
    status = Column(String, nullable=True)
    raw_log = Column(Text, nullable=False)

    log_hash = Column(String, nullable=True)
    previous_hash = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    rule_name = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    source_ip = Column(String, nullable=True)
    username = Column(String, nullable=True)
    event_count = Column(Integer, default=0)
    first_seen = Column(DateTime, nullable=True)
    last_seen = Column(DateTime, nullable=True)
    status = Column(String, default="open")
    created_at = Column(DateTime, default=datetime.utcnow)