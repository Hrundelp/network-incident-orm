from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Incident, IncidentStatus, NetworkDevice


class IncidentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(
        self,
        *,
        symptoms: str,
        devices: Sequence[NetworkDevice],
        probable_cause: str | None = None,
    ) -> Incident:
        if not devices:
            raise ValueError("Укажите хотя бы одно затронутое устройство")
        incident = Incident(
            symptoms=symptoms,
            devices=list(devices),
            probable_cause=probable_cause,
        )
        self.session.add(incident)
        self.session.flush()
        return incident

    def get(self, incident_id: int) -> Incident | None:
        return self.session.get(Incident, incident_id)

    def list_all(self) -> Sequence[Incident]:
        statement = select(Incident).order_by(Incident.id)
        return self.session.scalars(statement).all()

    def update(
        self,
        incident_id: int,
        *,
        status: IncidentStatus,
        probable_cause: str | None,
        resolution_result: str | None,
    ) -> Incident | None:
        incident = self.get(incident_id)
        if incident is None:
            return None
        incident.status = status
        incident.probable_cause = probable_cause
        incident.resolution_result = resolution_result
        return incident

    def delete(self, incident_id: int) -> bool:
        incident = self.get(incident_id)
        if incident is None:
            return False
        self.session.delete(incident)
        return True
