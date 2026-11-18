from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Enum, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.incident_device import incident_devices

if TYPE_CHECKING:
    from app.models.network_device import NetworkDevice
    from app.models.recovery_action import RecoveryAction


class IncidentStatus(StrEnum):
    OPEN = "open"
    RESOLVED = "resolved"
    ESCALATED = "escalated"


class Incident(Base):
    __tablename__ = "incidents"

    id: Mapped[int] = mapped_column(primary_key=True)
    detected_at: Mapped[datetime] = mapped_column(server_default=func.current_timestamp())
    symptoms: Mapped[str] = mapped_column(Text)
    probable_cause: Mapped[str | None] = mapped_column(Text)
    status: Mapped[IncidentStatus] = mapped_column(
        Enum(
            IncidentStatus,
            values_callable=lambda statuses: [status.value for status in statuses],
            native_enum=False,
            create_constraint=True,
            validate_strings=True,
            name="ck_incident_status",
        ),
        server_default=IncidentStatus.OPEN.value,
    )
    resolution_result: Mapped[str | None] = mapped_column(Text)

    devices: Mapped[list[NetworkDevice]] = relationship(
        secondary=incident_devices, back_populates="incidents", passive_deletes=True
    )
    recovery_actions: Mapped[list[RecoveryAction]] = relationship(
        back_populates="incident", cascade="all, delete-orphan", passive_deletes=True
    )
