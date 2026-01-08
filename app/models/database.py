"""
Database Models
SQLite database for storing conversations and bookings
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.config.settings import settings

Base = declarative_base()


class Conversation(Base):
    """
    Stores conversation sessions
    """
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True)
    
    # Patient info
    patient_name = Column(String(200))
    patient_phone = Column(String(50))
    patient_email = Column(String(200))
    patient_dob = Column(String(50))
    
    # Booking info
    service_type = Column(String(200))
    insurance = Column(String(200))
    patient_type = Column(String(50))  # new, existing, emergency
    urgency = Column(String(50))
    preferred_date = Column(String(100))
    preferred_time = Column(String(100))
    
    # Conversation data
    state = Column(String(50))
    messages = Column(Text)  # JSON string of message history
    is_complete = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Metadata
    source = Column(String(50))  # voice, chat, web
    notes = Column(Text)


class Booking(Base):
    """
    Stores confirmed bookings
    """
    __tablename__ = "bookings"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True)
    
    # Patient info
    patient_name = Column(String(200))
    patient_phone = Column(String(50))
    patient_email = Column(String(200))
    patient_dob = Column(String(50))
    
    # Appointment details
    service_type = Column(String(200))
    appointment_date = Column(String(100))
    appointment_time = Column(String(100))
    doctor = Column(String(200))
    
    # Status
    status = Column(String(50))  # pending, confirmed, cancelled, completed
    insurance = Column(String(200))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Notifications
    sms_sent = Column(Boolean, default=False)
    reminder_sent = Column(Boolean, default=False)
    
    # Notes
    notes = Column(Text)


# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

# Create all tables
Base.metadata.create_all(bind=engine)

# Create session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Dependency for getting database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


print("✅ Database initialized successfully!")