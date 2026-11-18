"""create incident journal

Revision ID: 82902967b2b4
Revises: base
Create Date: 2026-11-18 10:40:51.485315

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "82902967b2b4"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "incidents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "detected_at", sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False,
        ),
        sa.Column("symptoms", sa.Text(), nullable=False),
        sa.Column("probable_cause", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "open", "resolved", "escalated", name="ck_incident_status",
                native_enum=False, create_constraint=True,
            ),
            server_default="open",
            nullable=False,
        ),
        sa.Column("resolution_result", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "network_devices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("ip_address", sa.String(length=45), nullable=False),
        sa.Column("device_type", sa.String(length=30), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ip_address"),
    )
    op.create_table(
        "incident_devices",
        sa.Column("incident_id", sa.Integer(), nullable=False),
        sa.Column("device_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["device_id"], ["network_devices.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["incident_id"], ["incidents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("incident_id", "device_id"),
    )
    op.create_table(
        "recovery_actions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("incident_id", sa.Integer(), nullable=False),
        sa.Column(
            "performed_at", sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"), nullable=False,
        ),
        sa.Column("target", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("result", sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(["incident_id"], ["incidents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_recovery_actions_incident_id"), "recovery_actions", ["incident_id"]
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_recovery_actions_incident_id"), table_name="recovery_actions")
    op.drop_table("recovery_actions")
    op.drop_table("incident_devices")
    op.drop_table("network_devices")
    op.drop_table("incidents")
