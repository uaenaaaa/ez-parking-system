"""This module contains the models and operations for the audit logs."""

# pylint: disable=R0801

from sqlalchemy import Column, Integer, VARCHAR, DateTime, Enum, ForeignKey, BINARY
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.utils.db import session_scope


class AuditLog(Base):  # pylint: disable=too-few-public-methods
    """Model for audit logs."""

    __tablename__ = "audit_log"
    audit_id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(BINARY(16), nullable=False)
    action_type = Column(Enum("CREATE", "UPDATE", "DELETE"), nullable=False)
    performed_by = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    target_user = Column(Integer, ForeignKey("user.user_id"), nullable=True)
    details = Column(VARCHAR(255), nullable=False)
    performed_at = Column(DateTime, nullable=False)
    ip_address = Column(VARCHAR(15), nullable=False)
    user_performed_by = relationship(
        "User",
        back_populates="performed_audits",
        foreign_keys=[performed_by]
    )
    user_target = relationship(
        "User",
        back_populates="targeted_audits",
        foreign_keys=[target_user]
    )

    # user = relationship("User", back_populates="audit")
    def to_dict(self):  # pylint: disable=missing-function-docstring
        if self is None:
            return {}
        return {
            "audit_id": self.audit_id,
            "uuid": str(self.uuid),
            "action_type": self.action_type,
            "performed_by": self.performed_by,
            "target_user": self.target_user,
            "details": self.details,
            "performed_at": self.performed_at,
            "ip_address": self.ip_address
        }


class AuditLogRepository:  # pylint: disable=too-few-public-methods
    """Wraps the logic for creating, updating, and deleting audit logs."""
    @staticmethod
    def create_audit_log(log_data: dict):
        """Create a new audit log."""
        with session_scope() as session:
            new_audit_log = AuditLog(**log_data)
            session.add(new_audit_log)
            session.flush()
            return new_audit_log.audit_id

    @staticmethod
    def get_audit_log(audit_uuid: bytes):
        """Get an audit log by its UUID."""
        with session_scope() as session:
            audit_log = session.query(AuditLog).filter_by(uuid=audit_uuid).first()
            return audit_log.to_dict()

    @staticmethod
    def get_all_audit_logs():
        """Get all the audit logs."""
        with session_scope() as session:
            audit_logs = session.query(AuditLog).all()
            return [audit_log.to_dict() for audit_log in audit_logs]
