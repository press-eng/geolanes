import random
from datetime import datetime, timezone

from beanie import PydanticObjectId
from strawberry.types import Info

from lib.graphql.inputs.create_gl_admin_input import CreateGlAdminInput
from lib.graphql.inputs.create_otp_input import CreateOtpInput
from lib.graphql.inputs.delete_gl_admin_input import DeleteGlAdminInput
from lib.graphql.inputs.gl_admin_input import GlAdminInput
from lib.graphql.inputs.update_gl_admin_input import UpdateGlAdminInput
from lib.graphql.types.error import Error
from lib.helpers.gl_admin_helper import get_verified_gl_admin, gl_admin_model_to_type
from lib.models.customer_model import CustomerModel
from lib.models.enterprise_customer_model import EnterpriseCustomerModel
from lib.models.gl_admin_model import GlAdminModel
from lib.models.notification_event_model import NotificationEventModel
from lib.services import my_gmaps, mybcrypt, mysmtp
from lib.utils import is_valid_email, validate_then_handle


async def create_gl_admin(admin: CreateGlAdminInput, info: Info):
    try:
        verified_admin = await get_verified_gl_admin(info)
        if not verified_admin:
            return Error(status=403, message="Forbidden")

        if not is_valid_email(admin.email):
            return Error(status=400, message="Email format is invalid!")

        searched_admin = await GlAdminModel.find_one({"email": admin.email})
        if searched_admin:
            return Error(status=400, message="Email already in use!")

        if len(admin.password) < 8:
            return Error(
                status=400, message="Password must at least have eight characters!"
            )

        if len(admin.name) < 3:
            return Error(
                status=400, message="Customer name must have at least 3 characters!"
            )

        inserted_admin = await GlAdminModel.insert_one(
            GlAdminModel(
                name=admin.name,
                email=admin.email,
                password=mybcrypt.hashpw(admin.password),
                fcm_token=admin.fcm_token or None,
                fcm_token_updated_at=datetime.utcnow() if admin.fcm_token else None,
                source_id=str(verified_admin.id),
            )
        )
        return await gl_admin_model_to_type(inserted_admin)

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")


async def read_gl_admin(admin: GlAdminInput):
    async def read_gl_admin_by_email_passw(admin):
        searched_admin = await GlAdminModel.find_one(
            {
                "email": admin.email,
                "password": {"$exists": True},
                "deactivated": {"$in": [False, None]},
            }
        )
        if not searched_admin:
            return Error(status=401, message="Invalid email or password!")

        failed_attempts = searched_admin.failed_login_attempts or 0
        if failed_attempts >= 5:
            return Error(status=429, message="Too many failed login attempts!")

        if not mybcrypt.checkpw(admin.password, searched_admin.password):
            await searched_admin.set(
                {
                    GlAdminModel.failed_login_attempts: failed_attempts + 1,
                    GlAdminModel.latest_failed_login_attempt: datetime.now(
                        timezone.utc
                    ),
                }
            )

            return Error(status=401, message="Invalid email or password!")

        if admin.fcm_token:
            searched_admin.fcm_token = admin.fcm_token
            searched_admin.fcm_token_updated_at = datetime.now(timezone.utc)
            await searched_admin.save()

        return await gl_admin_model_to_type(searched_admin)

    async def read_gl_admin_by_email_otp(admin):
        searched_admin = await GlAdminModel.find_one(
            {
                "email": admin.email,
                "deactivated": {"$in": [False, None]},
            }
        )
        if not searched_admin:
            return Error(status=401, message="Invalid email or OTP!")

        failed_attempts = searched_admin.failed_login_attempts or 0
        if failed_attempts >= 5:
            return Error(status=429, message="Too many failed login attempts!")

        if searched_admin.otp != admin.otp:
            await searched_admin.set(
                {
                    GlAdminModel.failed_login_attempts: failed_attempts + 1,
                    GlAdminModel.latest_failed_login_attempt: datetime.now(
                        timezone.utc
                    ),
                }
            )

            return Error(status=401, message="Invalid email or OTP!")

        if admin.fcm_token:
            searched_admin.fcm_token = admin.fcm_token
            searched_admin.fcm_token_updated_at = datetime.now(timezone.utc)
            await searched_admin.save()

        await searched_admin.set(
            {
                GlAdminModel.otp: None,
                GlAdminModel.otp_created_at: None,
            }
        )

        return await gl_admin_model_to_type(searched_admin)

    validator_config = [
        {
            "args": ["email", "password"],
            "handler": read_gl_admin_by_email_passw,
        },
        {
            "args": ["email", "password", "fcm_token"],
            "handler": read_gl_admin_by_email_passw,
        },
        {
            "args": ["email", "otp"],
            "handler": read_gl_admin_by_email_otp,
        },
        {
            "args": ["email", "otp", "fcm_token"],
            "handler": read_gl_admin_by_email_otp,
        },
    ]

    try:
        return await validate_then_handle(validator_config, admin)

    except ValueError as e:
        return Error(status=400, message=str(e))

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")


async def update_gl_admin(admin: UpdateGlAdminInput, info: Info):
    try:
        searched_admin = await get_verified_gl_admin(info)
        if not searched_admin:
            return Error(status=403, message="Forbidden")

        if admin.password and len(admin.password) < 8:
            return Error(
                status=400, message="Password must at least have eight characters!"
            )

        if admin.gender and not admin.gender in ["male", "female"]:
            return Error(
                status=400, message='Gender must either be "male" or "female".'
            )

        existing_events = set(
            [str(n.id) for n in await NotificationEventModel.find_all().to_list()]
        )
        if admin.notification_events and not set(admin.notification_events).issubset(
            existing_events
        ):
            return Error(status=400, message="Invalid event ID!")

        if admin.password:
            searched_admin.password = mybcrypt.hashpw(admin.password)

        if admin.avatar_url:
            searched_admin.avatar_url = admin.avatar_url

        if admin.phone:
            searched_admin.phone = admin.phone

        if admin.gender:
            searched_admin.gender = admin.gender

        if admin.fcm_token:
            searched_admin.fcm_token = admin.fcm_token
            searched_admin.fcm_token_updated_at = datetime.now(timezone.utc)

        if admin.notification_events:
            searched_admin.notification_event_ids = admin.notification_events

        if admin.address:
            coords = await my_gmaps.find_place_coordinates(admin.address)
            if coords:
                searched_admin.address_latitude = coords[0]
                searched_admin.address_longitude = coords[1]

            searched_admin.address = admin.address

        if admin.name:
            searched_admin.name = admin.name

        searched_admin.updated_at = datetime.now(timezone.utc)
        await searched_admin.save()

        return await gl_admin_model_to_type(searched_admin)

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")


async def delete_gl_admin(admin: DeleteGlAdminInput, info: Info):
    try:
        verified_admin = await get_verified_gl_admin(info)
        if not verified_admin:
            return Error(status=403, message="Forbidden!")

        if admin.gl_admin_id:
            searched_admin = await GlAdminModel.find_one(
                {GlAdminModel.id: PydanticObjectId(admin.gl_admin_id)}
            )
            if not searched_admin:
                return Error(status=404, message="Admin not found!")

            if searched_admin.source_id != str(verified_admin.id):
                return Error(status=403, message="Forbidden!")

            if admin.permanent:
                searched_admin.permanently_deactivated = True

            searched_admin.deactivated = True
            searched_admin.updated_at = datetime.now(timezone.utc)
            await searched_admin.save()
            return Error(status=200, message="Admin deleted successfully!")

        if admin.permanent:
            verified_admin.permanently_deactivated = True

        verified_admin.deactivated = True
        verified_admin.updated_at = datetime.now(timezone.utc)
        await verified_admin.save()

        return Error(status=200, message="Admin deleted successfully!")

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")


async def create_gl_admin_otp(otp: CreateOtpInput):
    code = "".join([str(random.randint(0, 9)) for i in range(0, 6)])

    async def create_email_otp(admin):
        if is_valid_email(admin.email):
            searched_admin = await GlAdminModel.find_one({"email": admin.email})
            if not searched_admin:
                return Error(
                    status=404, message="No Admin registered with provided email!"
                )

            await searched_admin.set(
                {
                    GlAdminModel.otp: code,
                    GlAdminModel.otp_created_at: datetime.now(timezone.utc),
                }
            )
            await mysmtp.send_otp_email(code, admin.email)

            return Error(status=201, message="Admin OTP created successfully!")

        return Error(status=400, message="Email format is invalid!")

    async def create_phone_otp(input):
        return Error(status=501, message="Phone OTP support is coming soon!")

    config = [
        {
            "args": ["email"],
            "handler": create_email_otp,
        },
        {
            "args": ["phone"],
            "handler": create_phone_otp,
        },
    ]

    try:
        return await validate_then_handle(config, otp)

    except ValueError as e:
        return Error(status=400, message=str(e))

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")


async def show_dashboard_data(self, info: Info):
    # verified_admin = await get_verified_gl_admin(info)
    # if not verified_admin:
    #     return Error(status=403, message="Forbidden!")

    individual_customers_records = await CustomerModel.find().to_list(length=None)
    individual_customers_count = len(individual_customers_records)
    print("*****I : ", individual_customers_count)

    enterprise_customer_records = await EnterpriseCustomerModel.find(
        {"account_type": "Enterprise", "is_deleted": False}
    ).to_list(length=None)
    enterprise_customer_count = len(enterprise_customer_records)
    print("*****E : ", enterprise_customer_count)

    advisor_customer_records = await EnterpriseCustomerModel.find(
        {"account_type": "Advisor", "is_deleted": False}
    ).to_list(length=None)
    advisor_customer_count = len(advisor_customer_records)

    print("*****A : ", advisor_customer_count)

    return Error(status=200, message="successfully")
