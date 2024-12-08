""" Represents the banned plates in the database."""

from sqlalchemy import (
    Column,
    Integer,
    Text,
    TIMESTAMP,
    Boolean,
    ForeignKey,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.exc import DataError, IntegrityError, OperationalError, DatabaseError
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.utils.db import session_scope
from app.utils.engine import get_session
from app.utils.uuid_utility import UUIDUtility


class BanUser(Base):
    """Represents the banned users in the database."""
    
    __tablename__ = "ban_user"
    __table_args__ = {'schema': 'public'}
    
    ban_id = Column(Integer, primary_key=True, autoincrement=True, server_default=func.nextval('ban_user_ban_id_seq'))
    user_id = Column(Integer, ForeignKey("public.user.user_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    ban_reason = Column(Text, nullable=False)
    ban_start = Column(TIMESTAMP, nullable=False, default=func.current_timestamp())
    ban_end = Column(TIMESTAMP, nullable=True)
    is_permanent = Column(Boolean, nullable=False, default=False)
    banned_by = Column(Integer, ForeignKey("public.user.user_id", ondelete="SET NULL", onupdate="CASCADE"), nullable=True)
    created_at = Column(TIMESTAMP, default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, default=func.current_timestamp(), onupdate=func.current_timestamp())
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False, default=func.uuid_generate_v4())
    
    user = relationship("User", foreign_keys=[user_id])
    banned_by_user = relationship("User", foreign_keys=[banned_by])
    
    
    def __repr__(self):
        return f"<BanUser(ban_id={self.ban_id}, user_id={self.user_id}, ban_reason={self.ban_reason})>"
    
    def to_dict(self):
        if self is None:
            return {}
        uuid_utility = UUIDUtility()
        return {
            "ban_id": self.ban_id,
            "user_id": self.user_id,
            "ban_reason": self.ban_reason,
            "ban_start": self.ban_start,
            "ban_end": self.ban_end,
            "is_permanent": self.is_permanent,
            "banned_by": self.banned_by,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "uuid": uuid_utility.format_uuid(uuid_utility.binary_to_uuid(self.uuid)),
        }


class BannedPlateOperations:
    """Operations for the BannedPlate model."""

    @staticmethod
    def ban_plate(plate_number: str, reason: str, banned_by: int) -> None:
        """Ban a plate number."""
        session = get_session()
        try:
            banned_plate = BannedPlate(
                plate_number=plate_number, reason=reason, banned_by=banned_by
            )
            session.add(banned_plate)
            session.commit()
        except (
            DataError,
            IntegrityError,
            OperationalError,
            DatabaseError,
        ) as exception:
            session.rollback()
            raise exception
        finally:
            session.close()

    @staticmethod
    def unban_plate(plate_number: str) -> None:
        """Unban a plate number."""
        session = get_session()
        try:
            session.query(BannedPlate).filter(
                BannedPlate.plate_number == plate_number
            ).delete()
            session.commit()
        except (DataError, IntegrityError, OperationalError, DatabaseError) as exc:
            session.rollback()
            raise exc
        finally:
            session.close()

    @staticmethod
    def get_banned_plates() -> list[BannedPlate]:
        """Get all banned plates."""
        session = get_session()
        try:
            return session.query(BannedPlate).all()
        except (OperationalError, DatabaseError) as exc:
            raise exc
        finally:
            session.close()

    @staticmethod
    def get_banned_plate(plate_number: str) -> BannedPlate:
        """Get a banned plate by plate number."""
        session = get_session()
        try:
            return (
                session.query(BannedPlate)
                .filter(BannedPlate.plate_number == plate_number)
                .first()
            )
        except (OperationalError, DatabaseError) as e:
            raise e
        finally:
            session.close()

class BanUserRepository:
    @staticmethod
    def ban_user(data: dict):
        with session_scope() as session:
            ban_user = BanUser(**data)
            session.add(ban_user)
            session.commit()
            return ban_user.ban_id
        
    @staticmethod
    def unban_user(user_id: int):
        with session_scope() as session:
            session.query(BanUser).filter(BanUser.user_id == user_id).delete()
            session.commit()
            
    @staticmethod
    def update_banned_user(data: dict):
        with session_scope() as session:
            session.query(BanUser).filter(BanUser.user_id == data["user_id"]).update(data)
            session.commit()
            
    @staticmethod
    def get_ban_user(user_id: int):
        with session_scope() as session:
            ban_user = session.query(BanUser).filter(BanUser.user_id == user_id).first()
            return ban_user.to_dict()
        
    @staticmethod
    def get_banned_users():
        with session_scope() as session:
            ban_users = session.query(BanUser).all()
            return [ban_user.to_dict() for ban_user in ban_users]
