""" Wraps the error handlers for the authentication related errors. """

from app.exceptions.authorization_exceptions import (
    EmailNotFoundException,
    MissingFieldsException,
    InvalidPhoneNumberException,
    PhoneNumberAlreadyTaken,
    EmailAlreadyTaken,
    IncorrectOTPException,
    ExpiredOTPException,
)

from app.utils.error_handlers.base_error_handler import handle_error


def handle_email_not_found(error):
    """This function handles email not found exceptions."""
    if isinstance(error, EmailNotFoundException):
        return handle_error(
            error,
            404,
            "email_not_found",
            "The email address you provided does not exist.",
        )
    raise error


def handle_missing_fields(error):
    """This function handles missing fields exceptions."""
    if isinstance(error, MissingFieldsException):
        return handle_error(
            error,
            400,
            "missing_fields",
            "Please provide all the required fields.",
        )
    raise error


def handle_invalid_phone_number(error):
    """This function handles invalid phone number exceptions."""
    if isinstance(error, InvalidPhoneNumberException):
        return handle_error(
            error,
            400,
            "invalid_phone_number",
            "Please provide a valid phone number.",
        )
    raise error


def handle_email_already_taken(error):
    """This function handles email already taken exceptions."""
    if isinstance(error, EmailAlreadyTaken):
        return handle_error(
            error,
            400,
            "email_already_taken",
            "Email already taken.",
        )
    raise error


def handle_phone_number_already_taken(error):
    """This function handles phone number already taken exceptions."""
    if isinstance(error, PhoneNumberAlreadyTaken):
        return handle_error(
            error,
            400,
            "phone_number_already_taken",
            "Phone number already taken.",
        )
    raise error


def handle_incorrect_otp(error):
    """This function handles incorrect OTP exceptions."""
    if isinstance(error, IncorrectOTPException):
        return handle_error(
            error,
            400,
            "incorrect_otp",
            "Incorrect OTP.",
        )
    raise error


def handle_expired_otp(error):
    """This function handles expired OTP exceptions."""
    if isinstance(error, ExpiredOTPException):
        return handle_error(
            error,
            400,
            "expired_otp",
            "Expired OTP.",
        )
    raise error