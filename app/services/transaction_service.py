"""This module contains the services for the transaction operations."""

from datetime import datetime
from uuid import uuid4

from app.exceptions.qr_code_exceptions import QRCodeError
from app.exceptions.slot_lookup_exceptions import SlotStatusTaken
from app.utils.uuid_utility import UUIDUtility
from app.models.parking_establishment import ParkingEstablishmentRepository
from app.models.parking_slot import ParkingSlotRepository
from app.models.parking_transaction import ParkingTransactionOperation, ParkingTransactionRepository
from app.models.user import UserRepository
from app.utils.qr_utils.generate_transaction_qr_code import QRCodeUtils


class TransactionService:  # pylint: disable=too-few-public-methods
    """Wraps the service actions for parking transaction operations"""

    @staticmethod
    def reserve_slot(reservation_data):
        """Reserves the slot for a user."""
        return SlotActionsService.reserve_slot(reservation_data)

    @staticmethod
    def verify_reservation_code(qr_content: str):
        """Verifies the reservation code for a user."""
        return TransactionVerification.verify_entry_transaction(qr_content)

    @staticmethod
    def verify_exit_code(exit_code):
        """Verifies the exit code for a user."""
        return TransactionVerification.verify_exit_transaction(exit_code)

    @staticmethod
    def occupy_slot(parking_data):
        """Occupies the slot for a user."""

    @staticmethod
    def release_slot(slot_data):
        """Releases the slot for a user."""

    @staticmethod
    def cancel_transaction(transaction_uuid: bytes):
        """Cancels the transaction for a user."""
        return SlotActionsService.cancel_transaction(transaction_uuid)

    @staticmethod
    def get_transaction_details_from_qr_code(qr_code_data):
        """Get the transaction details from a QR code."""
        return TransactionVerification.get_transaction_details_from_qr_code(qr_code_data)

    @staticmethod
    def view_transaction(transaction_uuid: bytes):
        """View the transaction for a user."""
        return SlotActionsService.view_transaction(transaction_uuid)

    @staticmethod
    def get_transaction_form_details(establishment_uuid: bytes, slot_code: str):
        """Get the transaction form details for a user."""
        return TransactionFormDetails.get_transaction_form_details(
            establishment_uuid, slot_code
        )

    @staticmethod
    def get_all_user_transactions(user_id):
        """Get all the transactions for a user."""
        return Transaction.get_all_user_transactions(user_id)


class SlotActionsService:  # pylint: disable=too-few-public-methods
    """Wraps the service actions for slot operations"""

    @staticmethod
    def reserve_slot(slot_reservation_data):
        """Reserves the slot for a user."""
        now = datetime.now()
        slot_reservation_data.update({"uuid": uuid4().bytes})
        slot_reservation_data.update({"created_at": now})
        slot_reservation_data.update({"updated_at": now})
        return ParkingTransactionOperation.add_new_transaction_entry(slot_reservation_data)

    @staticmethod
    def release_slot(slot_data):
        """Releases the slot for a user."""

    @staticmethod
    def cancel_transaction(transaction_uuid: bytes):
        """Cancels the transaction for a user."""
        return ParkingTransactionRepository.update_transaction_status(
            transaction_uuid, "cancelled"
        )

    @staticmethod
    def view_transaction(transaction_uuid: bytes):
        """View the transaction for a user."""
        transaction_data = ParkingTransactionOperation.get_transaction(transaction_uuid)
        if transaction_data.get("status") not in ["active", "reserved"]:
            return {"transaction_data": transaction_data}
        qr_code_utils = QRCodeUtils()
        qr_data = qr_code_utils.generate_qr_content(
            data={
                "uuid": transaction_data.get("uuid"),
                "status": transaction_data.get("status"),
                "plate_number": transaction_data.get("plate_number"),
            }
        )
        base64_image = qr_code_utils.generate_qr_code(qr_data)
        return {"transaction_data": transaction_data, "qr_code": base64_image}


class TransactionVerification:
    """Wraps the service actions for transaction verification operations"""

    @staticmethod
    def verify_entry_transaction(transaction_qr_code_data):
        """Verifies the entry transaction for a user."""
        qr_code_utils = QRCodeUtils()
        transaction_data = qr_code_utils.verify_qr_content(transaction_qr_code_data)
        if transaction_data.get("status") != "reserved":
            raise QRCodeError("Invalid transaction status.")
        transaction_uuid = UUIDUtility().uuid_to_binary(transaction_data.get("uuid"))
        return ParkingTransactionRepository.update_transaction_status(
            transaction_uuid, "active",
        )

    @staticmethod
    def verify_exit_transaction(transaction_qr_code_data):
        """Verifies the exit transaction for a user."""
        qr_code_utils = QRCodeUtils()
        transaction_data = qr_code_utils.verify_qr_content(transaction_qr_code_data)
        if transaction_data.get("status") != "active":
            raise QRCodeError("Invalid transaction status.")

    @staticmethod
    def get_transaction_details_from_qr_code(qr_code_data):
        """Get the transaction details from a QR code."""
        qr_code_utils = QRCodeUtils()
        uuid_utils = UUIDUtility()
        transaction_data = qr_code_utils.verify_qr_content(qr_code_data)
        transaction_uuid = transaction_data.get("uuid")
        transaction_data = ParkingTransactionRepository.get_transaction(
            transaction_uuid=uuid_utils.uuid_to_binary(transaction_uuid)
        )
        user_id = transaction_data.get("user_id")
        user_info = UserRepository.get_user(user_id=user_id)
        return {
            "transaction_uuid": transaction_uuid,
            "user_info": user_info,
            "transaction_data": transaction_data,
        }


class TransactionFormDetails:  # pylint: disable=too-few-public-methods
    """Wraps the service actions for transaction form details operations"""

    @staticmethod
    def get_transaction_form_details(establishment_uuid_bin: bytes, slot_code: str):
        """
        Get the transaction form details for a user.

        Args:
            establishment_uuid_bin (bin): UUID of the establishment
            slot_code (str): Slot code identifier

        Raises:
            SlotStatusTaken: If slot is not available
            ValueError: If UUID format is invalid
        """
        status = ParkingSlotRepository().get_slot(slot_code).get("status")
        if status in ["reserved", "occupied"]:
            raise SlotStatusTaken("Invalid slot status.")

        establishment_info = ParkingEstablishmentRepository.get_establishment(
            establishment_uuid=establishment_uuid_bin
        )

        slot_info = ParkingSlotRepository.get_slot(slot_code)
        return {"establishment_info": establishment_info, "slot_info": slot_info}


class Transaction:  # pylint: disable=too-few-public-methods
    """Wraps the service actions for transaction operations"""

    @staticmethod
    def get_all_user_transactions(user_id):
        """Get all the transactions for a user."""
        return ParkingTransactionRepository.get_all_transactions(user_id=user_id)
