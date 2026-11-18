from pathlib import Path
from sqlite3 import Connection

from sqlalchemy import URL, create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


database_path = Path(__file__).resolve().parent.parent / "network_incidents.db"
engine = create_engine(
    URL.create("sqlite", database=str(database_path)),
    connect_args={"autocommit": False},
)
SessionLocal = sessionmaker(bind=engine)


@event.listens_for(engine, "connect")
def enable_foreign_keys(connection: Connection, _record: object) -> None:
    # SQLite applies this setting per connection and outside a transaction.
    previous_autocommit = connection.autocommit
    connection.autocommit = True
    try:
        connection.execute("PRAGMA foreign_keys=ON").close()
    finally:
        connection.autocommit = previous_autocommit
