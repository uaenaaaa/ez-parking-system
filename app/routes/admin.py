""" Wraps all the admin routes. """

# pylint: disable=missing-function-docstring, missing-class-docstring

from functools import wraps

from flask_jwt_extended import jwt_required, get_jwt
from flask_smorest import Blueprint
from flask.views import MethodView

from app.schema.ban_query_validation import BanQueryValidation
from app.schema.parking_manager_validation import CreateSlotSchema, UpdateSlotSchema
from app.services.admin_service import AdminService
from app.utils.response_util import set_response


admin_blp = Blueprint(
    "admin",
    "admin",
    url_prefix="/api/v1/admin",
    description="Admin API for EZ Parking System Frontend",
)


def admin_role_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            jwt_data = get_jwt()
            is_admin = jwt_data.get("role") == "admin"
            if not is_admin:
                return set_response(
                    401, {"code": "unauthorized", "message": "Admin required."}
                )
            admin_id = jwt_data.get("sub", {}).get("user_id")
            return fn(admin_id=admin_id, *args, **kwargs)

        return decorator

    return wrapper


@admin_blp.route("/ban-plate-number")
class BanPlateNumber(MethodView):
    @admin_blp.arguments(BanQueryValidation)
    @admin_blp.response(200, {"message": str})
    @admin_blp.doc(
        security=[{"Bearer": []}],
        description="Ban a plate number.",
        responses={
            200: "Plate number banned.",
            401: "Unauthorized",
            403: "Forbidden",
            500: "Internal Server Error",
            422: "Unprocessable",
        },
    )
    @admin_role_required()
    @jwt_required(False)
    def post(self, ban_data, admin_id):
        admin_service = AdminService()
        ban_data["banned_by"] = admin_id
        admin_service.ban_plate_number(ban_data)
        return set_response(201, {"code": "success", "message": "Plate number banned."})


@admin_blp.route("/unban-plate-number")
class UnbanPlateNumber(MethodView):
    @admin_blp.arguments(BanQueryValidation)
    @admin_blp.response(200, {"message": str})
    @admin_blp.doc(
        security=[{"Bearer": []}],
        description="Unban a plate number.",
        responses={
            200: "Plate number unbanned.",
            401: "Unauthorized",
            403: "Forbidden",
            500: "Internal Server Error",
            422: "Unprocessable",
        },
    )
    @admin_role_required()
    @jwt_required(False)
    def post(self, ban_data, admin_id):
        admin_service = AdminService()
        print(admin_id)
        admin_service.unban_plate_number(ban_data["plate_number"])
        return set_response(
            201, {"code": "success", "message": "Plate number unbanned."}
        )


@admin_blp.route("/add-slot")
class AddSlot(MethodView):
    @admin_blp.arguments(CreateSlotSchema)
    @admin_blp.response(200, {"message": str})
    @admin_blp.doc(
        security=[{"Bearer": []}],
        description="Add a slot.",
        responses={
            200: "Slot added.",
            401: "Unauthorized",
            403: "Forbidden",
            500: "Internal Server Error",
            422: "Unprocessable",
        },
    )
    @jwt_required(False)
    @admin_role_required()
    def post(self, slot_data, admin_id):
        print(slot_data)
        admin_service = AdminService()
        print(admin_id)  # this is for auditing
        admin_service.add_slot(slot_data)
        return set_response(201, {"code": "success", "message": "Slot added."})


@admin_blp.route("/update-slot")
class UpdateParkingSlot(MethodView):

    @admin_blp.arguments(UpdateSlotSchema)
    @admin_blp.response(200, {"message": str})
    @admin_blp.doc(
        security=[{"Bearer": []}],
        description="Update a parking slot.",
        responses={
            200: "Parking slot updated.",
            401: "Unauthorized",
            403: "Forbidden",
            500: "Internal Server Error",
            422: "Unprocessable",
        },
    )
    @jwt_required(False)
    @admin_role_required()
    def patch(self, slot_data, admin_id):
        admin_service = AdminService()
        print(admin_id)  # this is for auditing
        admin_service.update_parking_slot(slot_data)
        return set_response(
            201, {"code": "success", "message": "Parking slot updated."}
        )
