from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    remind_at = Column(DateTime, nullable=False)
    message = Column(String, nullable=True)
    is_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, nullable=False)
