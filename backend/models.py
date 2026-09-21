from datetime import datetime, timezone
from sqlalchemy import String, Text, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

def now():
    return datetime.now(timezone.utc)

class Content(Base):
    __tablename__ = "content"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    brand: Mapped[str] = mapped_column(String(100))
    platform: Mapped[str] = mapped_column(String(50))
    objective: Mapped[str] = mapped_column(String(100))
    topic: Mapped[str] = mapped_column(String(300))
    language: Mapped[str] = mapped_column(String(50), default="English")
    content: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(50), default="pending_review")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)

class Lead(Base):
    __tablename__ = "leads"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    company: Mapped[str] = mapped_column(String(200))
    industry: Mapped[str] = mapped_column(String(100))
    location: Mapped[str] = mapped_column(String(150))
    fit_score: Mapped[float] = mapped_column(Float)
    source_url: Mapped[str] = mapped_column(String(1000), default="")
    outreach: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)

class Review(Base):
    __tablename__ = "reviews"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content_id: Mapped[int] = mapped_column(ForeignKey("content.id"))
    decision: Mapped[str] = mapped_column(String(30))
    comments: Mapped[str] = mapped_column(Text, default="")
    reviewed_at: Mapped[datetime] = mapped_column(DateTime, default=now)

class Feedback(Base):
    __tablename__ = "feedback"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content_id: Mapped[int] = mapped_column(ForeignKey("content.id"))
    reason: Mapped[str] = mapped_column(String(100))
    details: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)

class ComplianceResult(Base):
    __tablename__ = "compliance_results"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content_id: Mapped[int] = mapped_column(ForeignKey("content.id"))
    status: Mapped[str] = mapped_column(String(30))
    issues: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
