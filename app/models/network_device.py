from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.incident_device import incident_devices

if TYPE_CHECKING:
    from app.models.incident import Incident


class NetworkDevice(Base):
    __tablename__ = "network_devices"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    ip_address: Mapped[str] = mapped_column(String(45), unique=True)
    device_type: Mapped[str] = mapped_column(String(30))

    incidents: Mapped[list[Incident]] = relationship(
        secondary=incident_devices, back_populates="devices", passive_deletes=True
    )
