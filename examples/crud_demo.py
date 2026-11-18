from sqlalchemy import func, select

from app.db import SessionLocal
from app.models import IncidentStatus, NetworkDevice, RecoveryAction
from app.models.incident_device import incident_devices
from app.repositories.incident_repository import IncidentRepository


def main() -> None:
    # TEST-NET-1 addresses keep real network addresses out of the demo.
    demo_devices = (
        ("192.0.2.10", "SW-DEMO", "switch"),
        ("192.0.2.11", "PLC-DEMO", "controller"),
    )

    with SessionLocal.begin() as session:
        devices = []
        for address, name, device_type in demo_devices:
            device = session.scalar(
                select(NetworkDevice).where(NetworkDevice.ip_address == address)
            )
            if device is None:
                device = NetworkDevice(name=name, ip_address=address, device_type=device_type)
            devices.append(device)

        repository = IncidentRepository(session)
        incident = repository.create(
            symptoms="[ДЕМО] Контроллер недоступен с рабочего места",
            devices=devices,
        )
        incident_id = incident.id
        device_ids = {device.id for device in devices}
    print(f"CREATE: создан инцидент №{incident_id}, статус open")

    with SessionLocal.begin() as session:
        repository = IncidentRepository(session)
        incident = repository.get(incident_id)
        assert incident is not None and incident.status == IncidentStatus.OPEN
        assert incident.probable_cause is None
        assert {device.id for device in incident.devices} == device_ids
        assert any(item.id == incident_id for item in repository.list_all())
        print(f"READ: инцидент в журнале, затронуто устройств: {len(incident.devices)}")

        repository.update(
            incident_id,
            status=IncidentStatus.RESOLVED,
            probable_cause="Настройка учебного порта отличается от утверждённой",
            resolution_result="Повторная проверка подтвердила доступность контроллера",
        )
        incident.recovery_actions.append(
            RecoveryAction(
                target="Учебный порт SW-DEMO/1",
                description="Восстановление утверждённой настройки порта (имитация)",
                result="Настройка восстановлена в демонстрационном сценарии",
            )
        )

    with SessionLocal.begin() as session:
        repository = IncidentRepository(session)
        incident = repository.get(incident_id)
        assert incident is not None and incident.status == IncidentStatus.RESOLVED
        assert incident.resolution_result and len(incident.recovery_actions) == 1
        print(f"UPDATE: статус {incident.status.value}, записано 1 действие")

    with SessionLocal.begin() as session:
        repository = IncidentRepository(session)
        # Leave relationships unloaded to exercise SQLite ON DELETE CASCADE.
        deleted = repository.delete(incident_id)
        assert deleted

    with SessionLocal() as session:
        repository = IncidentRepository(session)
        assert repository.get(incident_id) is None
        assert not repository.delete(incident_id)
        assert session.scalar(
            select(func.count()).select_from(RecoveryAction)
            .where(RecoveryAction.incident_id == incident_id)
        ) == 0
        assert session.scalar(
            select(func.count()).select_from(incident_devices)
            .where(incident_devices.c.incident_id == incident_id)
        ) == 0
        assert {device.id for device in session.scalars(
            select(NetworkDevice).where(NetworkDevice.id.in_(device_ids))
        )} == device_ids
    print("DELETE: инцидент, действие и связи удалены, устройства сохранены")
    print("CRUD: все проверки пройдены")


if __name__ == "__main__":
    main()
