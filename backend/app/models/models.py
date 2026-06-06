from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, DateTime, ForeignKey, Text, JSON
from datetime import datetime
import uuid

class Base(DeclarativeBase):
    pass

class Partner(Base):
    __tablename__ = "partner"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

class YouTubeChannel(Base):
    __tablename__ = "youtube_channel"

    id: Mapped[str] = mapped_column(primary_key=True) # Channel ID from YouTube
    partner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("partner.id"))
    title: Mapped[str] = mapped_column(String(255))
    credentials: Mapped[dict] = mapped_column(JSON) # OAuth2 tokens
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

class TranslationTask(Base):
    __tablename__ = "translation_task"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    channel_id: Mapped[str] = mapped_column(ForeignKey("youtube_channel.id"))
    source_url: Mapped[str] = mapped_column(Text)
    target_language: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), default="pending") # pending, processing, review_required, completed, failed

    # HITL Data
    transcript_json: Mapped[dict] = mapped_column(JSON, nullable=True) # Full timestamped transcript for editor

    # Metadata
    source_metadata: Mapped[dict] = mapped_column(JSON, nullable=True)
    translated_metadata: Mapped[dict] = mapped_column(JSON, nullable=True)

    # File Paths
    local_source_path: Mapped[str] = mapped_column(Text, nullable=True)
    local_final_path: Mapped[str] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)

class TaskLog(Base):
    __tablename__ = "task_log"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("translation_task.id"))
    event: Mapped[str] = mapped_column(String(255)) # started, completed, failed
    metrics: Mapped[dict] = mapped_column(JSON, nullable=True) # {gpu_time: 120, cost: 0.05}
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

class PartnershipAgreement(Base):
    __tablename__ = "partnership_agreement"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    channel_id: Mapped[str] = mapped_column(ForeignKey("youtube_channel.id"))
    share_percentage: Mapped[float] = mapped_column(default=50.0) # E.g., 50.0 for 50/50
    status: Mapped[str] = mapped_column(String(50), default="active") # active, terminated
    terms_signed_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

class RevenueReport(Base):
    __tablename__ = "revenue_report"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    channel_id: Mapped[str] = mapped_column(ForeignKey("youtube_channel.id"))
    month: Mapped[str] = mapped_column(String(7)) # YYYY-MM
    gross_revenue: Mapped[float] = mapped_column(default=0.0)
    processing_costs: Mapped[float] = mapped_column(default=0.0)
    net_profit: Mapped[float] = mapped_column(default=0.0)
    partner_payout: Mapped[float] = mapped_column(default=0.0)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
