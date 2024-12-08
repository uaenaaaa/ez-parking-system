""" Parking transaction module that represents the parking transaction database table. """

# pylint: disable=R0401, R0801, C0415

from typing import Literal

from sqlalchemy import (
    VARCHAR,
    Column,
    Enum,
    Integer,
    ForeignKey,
    DateTime,
    BINARY,
    DECIMAL,
    update,
)
from sqlalchemy.exc import DataError, DatabaseError, IntegrityError, OperationalError
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.utils.engine import get_session
from app.utils.uuid_utility import UUIDUtility


class ParkingTransaction(Base):  # pylint: disable=R0903
    """
    SQLAlchemy model representing a parking transaction record.

    Contains details about a parking event including vehicle info, timing,
    slot allocation, payment status and associated relationships with
    slot and vehicle type tables.
    """

    __tablename__ = "parking_transaction"

    transaction_id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(BINARY(16), nullable=False)
    slot_id = Column(Integer, ForeignKey("slot.slot_id"), nullable=False)
    vehicle_type_id = Column(
        Integer, ForeignKey("vehicle_type.vehicle_id"), nullable=False
    )
    plate_number = Column(VARCHAR(15), nullable=False)
    entry_time = Column(DateTime, nullable=True)
    exit_time = Column(DateTime, nullable=True)
    amount_due = Column(DECIMAL(9, 2), nullable=True)
    payment_status = Column(
        Enum("pending", "partially_paid", "paid", "overdue"),
        nullable=False,
        default="pending",
    )
    status = Column(
        Enum("reserved", "active", "completed", "cancelled"),
        nullable=False,
        default="reserved",
    )

    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    slot = relationship("Slot", back_populates="parking_transaction")
    vehicle_type = relationship("VehicleType", back_populates="parking_transaction")

    def to_dict(self):
        """
        Convert the model instance to a dictionary.
        """
        return {
            "transaction_id": self.transaction_id,
            "uuid": self.uuid.hex(),
            "slot_id": self.slot_id,
            "vehicle_type_id": self.vehicle_type_id,
            "plate_number": self.plate_number,
            "entry_time": self.entry_time is not None
            and self.entry_time.strftime("%Y-%m-%d %H:%M:%S")
            or "Not Available",
            "exit_time": self.exit_time is not None
            and self.exit_time.strftime("%Y-%m-%d %H:%M:%S")
            or "Not Available",
            "amount_due": self.amount_due,
            "payment_status": str(self.payment_status).capitalize(),
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class ParkingTransactionOperation:
    """Class that provides operations for parking transactions in the database."""

    @classmethod
    def get_transaction_by_plate_number(cls, plate_number: str):
        """
        Retrieve a parking transaction from the database by the vehicle plate number.
        Returns dictionary with transaction details including related slot and vehicle info.
        """
        from app.models.slot import Slot
        from app.models.vehicle_type import VehicleType

        session = get_session()
        try:
            uuid_utility = UUIDUtility()
            transactions = (
                session.query(ParkingTransaction)
                .join(Slot, Slot.slot_id == ParkingTransaction.slot_id)
                .join(
                    VehicleType,
                    VehicleType.vehicle_id == ParkingTransaction.vehicle_type_id,
                )
                .filter(ParkingTransaction.plate_number == plate_number)
                .all()
            )
            if not transactions:
                return {}
            return {
                "transactions": [
                    {
                        "uuid": uuid_utility.format_uuid(
                            uuid_utility.binary_to_uuid(transaction.uuid)
                        ),
                        "status": transaction.status,
                        "payment_status": str(transaction.payment_status).capitalize(),
                        "slot_details": {
                            "slot_code": transaction.slot.slot_code,
                            "slot_status": transaction.slot.slot_status,
                            "slot_features": str(
                                transaction.slot.slot_features
                            ).capitalize(),
                            "floor_level": transaction.slot.floor_level,
                            "slot_multiplier": float(transaction.slot.slot_multiplier),
                            "is_premium": transaction.slot.is_premium == 1
                            and "Yes"
                            or "No",
                        },
                        "vehicle_details": {
                            "type_name": transaction.vehicle_type.name,
                            "size_category": transaction.vehicle_type.size_category,
                            "base_rate_multiplier": float(
                                transaction.vehicle_type.base_rate_multiplier
                            ),
                        },
                    }
                    for transaction in transactions
                ]
            }

        except (DatabaseError, OperationalError) as error:
            raise error
        finally:
            session.close()

    @classmethod
    def get_transaction(cls, transaction_uuid_bin: bytes):
        """
        Retrieve a parking transaction from the database by its UUID.
        Returns dictionary with transaction details including related slot and vehicle info.
        """
        from app.models.slot import Slot
        from app.models.vehicle_type import VehicleType
        from app.models.parking_establishment import ParkingEstablishment

        session = get_session()
        try:
            transaction = (
                session.query(ParkingTransaction)
                .join(Slot, Slot.slot_id == ParkingTransaction.slot_id)
                .join(
                    VehicleType,
                    VehicleType.vehicle_id == ParkingTransaction.vehicle_type_id,
                )
                .filter(ParkingTransaction.uuid == transaction_uuid_bin)
                .first()
            )
            establishment_info = (
                session.query(
                    ParkingEstablishment.name,
                    ParkingEstablishment.address,
                    ParkingEstablishment.longitude,
                    ParkingEstablishment.latitude,
                    ParkingEstablishment.contact_number,
                )
                .join(
                    Slot, Slot.establishment_id == ParkingEstablishment.establishment_id
                )
                .filter(Slot.slot_id == transaction.slot_id)
                .first()
            )

            if not transaction:
                return {}
            transaction_dict = transaction.to_dict()
            transaction_dict.update(
                {
                    "uuid": UUIDUtility().format_uuid(
                        UUIDUtility().binary_to_uuid(transaction.uuid)
                    ),
                    "slot_details": {
                        "slot_code": transaction.slot.slot_code,
                        "slot_status": transaction.slot.slot_status,
                        "slot_features": str(
                            transaction.slot.slot_features
                        ).capitalize(),
                        "floor_level": transaction.slot.floor_level,
                        "slot_multiplier": float(transaction.slot.slot_multiplier),
                        "is_premium": transaction.slot.is_premium == 1
                        and "Yes"
                        or "No",
                    },
                    "vehicle_details": {
                        "type_name": transaction.vehicle_type.name,
                        "size_category": transaction.vehicle_type.size_category,
                        "base_rate_multiplier": float(
                            transaction.vehicle_type.base_rate_multiplier
                        ),
                    },
                    "establishment_info": {
                        "name": establishment_info.name,
                        "address": establishment_info.address,
                        "longitude": establishment_info.longitude,
                        "latitude": establishment_info.latitude,
                        "contact_number": establishment_info.contact_number,
                    },
                }
            )

            return transaction_dict

        except (DatabaseError, OperationalError) as error:
            raise error
        finally:
            session.close()

    @classmethod
    def add_new_transaction_entry(cls, transaction_data):
        """
        Add a new parking transaction entry to the database.
        """
        from app.models import Slot

        session = get_session()
        try:
            transaction = ParkingTransaction(
                uuid=transaction_data.get("uuid"),
                slot_id=transaction_data.get("slot_id"),
                vehicle_type_id=transaction_data.get("vehicle_type_id"),
                plate_number=transaction_data.get("plate_number"),
                entry_time=transaction_data.get("entry_time"),
                exit_time=transaction_data.get("exit_time"),
                created_at=transaction_data.get("created_at"),
                updated_at=transaction_data.get("updated_at"),
            )

            session.execute(
                update(Slot)
                .values(slot_status="occupied")
                .where(Slot.slot_id == transaction_data.get("slot_id"))
            )

            session.add(transaction)
            session.commit()
        except (DatabaseError, DataError, IntegrityError, OperationalError) as e:
            session.rollback()
            raise e
        finally:
            session.close()


class UpdateTransaction:  # pylint: disable=R0903
    """Class that provides operations for updating parking transactions in the database."""

    @classmethod
    def update_transaction_entry(cls, transaction_id, transaction_data):
        """
        Update a parking transaction entry in the database.
        """

    @classmethod
    def update_transaction_status(
        cls, transaction_status: Literal["active", "completed"], transaction_uuid: str
    ):
        """
        Update the status of a parking transaction in the database.
        """
        from app.models import Slot

        session = get_session()
        try:
            transaction_uuid_bin = bytes.fromhex(transaction_uuid)
            session.execute(
                update(ParkingTransaction)
                .values(status=transaction_status)
                .where(ParkingTransaction.uuid == transaction_uuid_bin)
            )
            transaction_slot = (
                session.query(ParkingTransaction)
                .filter(ParkingTransaction.uuid == transaction_uuid_bin)
                .first()
            )
            session.execute(
                update(Slot)
                .values(slot_status="occupied")
                .where(Slot.slot_id == transaction_slot.slot_id)  # type: ignore
            )
            session.commit()
        except (DatabaseError, DataError, IntegrityError, OperationalError) as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def cancel_transaction(cls, transaction_uuid: bytes):
        """
        Cancel a parking transaction in the database.
        """
        session = get_session()
        try:
            session.execute(
                update(ParkingTransaction)
                .values(status="cancelled")
                .where(ParkingTransaction.uuid == transaction_uuid)
            )
            session.commit()
        except (DatabaseError, DataError, IntegrityError, OperationalError) as e:
            session.rollback()
            raise e
        finally:
            session.close()


class DeleteTransaction:  # pylint: disable=R0903
    """Class that provides operations for deleting parking transactions in the database."""

    @classmethod
    def delete_transaction_entry(cls, transaction_id):
        """
        Delete a parking transaction entry from the database.
        """
        session = get_session()
        try:
            transaction = session.query(ParkingTransaction).get(transaction_id)
            session.delete(transaction)
            session.commit()
        except (DatabaseError, DataError, IntegrityError, OperationalError) as e:
            session.rollback()
            raise e
        finally:
            session.close()


class FeeOperation:  # pylint: disable=R0903
    """Class that provides operations for calculating parking fees."""
