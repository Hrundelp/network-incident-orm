from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base

if TYPE_CHECKING:
    from app.models.incident import Incident


class RecoveryAction(Base):
    __tablename__ = "recovery_actions"

    id: Mapped[int] = mapped_column(primary_key=True)
    incident_id: Mapped[int] = mapped_column(
        ForeignKey("incidents.id", ondelete="CASCADE"), index=True
    )
    performed_at: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    target: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    result: Mapped[str] = mapped_column(Text)

    incident: Mapped[Incident] = relationship(back_populates="recovery_actions")
