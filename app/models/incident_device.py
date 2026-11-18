from sqlalchemy import Column, ForeignKey, Table

from app.db import Base

incident_devices = Table(
    "incident_devices",
    Base.metadata,
    Column("incident_id", ForeignKey("incidents.id", ondelete="CASCADE"), primary_key=True),
    Column("device_id", ForeignKey("network_devices.id", ondelete="CASCADE"), primary_key=True),
)
