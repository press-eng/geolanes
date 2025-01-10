import random
from datetime import datetime, timezone

import strawberry
from babel import numbers
from iso_language_codes import language_name
from pycountry import countries
from strawberry.types import Info

from lib import config
from lib.graphql.inputs.all_customers_input import AllCustomersInput
from lib.graphql.inputs.create_customer_input import CreateCustomerInput
from lib.graphql.inputs.create_otp_input import CreateOtpInput
from lib.graphql.inputs.customer_input import CustomerInput
from lib.graphql.inputs.delete_customer_input import DeleteCustomerInput
from lib.graphql.inputs.update_customer_input import UpdateCustomerInput
from lib.graphql.types.all_customers_page import AllCustomersPage
from lib.graphql.types.error import Error
from lib.helpers.customer_helper import customer_model_to_type, get_verified_customer
from lib.helpers.gl_admin_helper import get_verified_gl_admin, gl_admin_model_to_type
from lib.models.customer_model import CustomerModel
from lib.models.hobby_model import HobbyModel
from lib.models.notification_event_model import NotificationEventModel
from lib.models.profession_model import ProfessionModel
from lib.models.sightseeing_model import SightseeingModel
from lib.services import (
    my_apple_auth,
    my_fb_auth,
    my_gmaps,
    my_google_auth,
    mybcrypt,
    mysmtp,
)
from lib.travelling_units import travelling_units
from lib.utils import is_valid_email, validate_then_handle


async def create_customer(customer: CreateCustomerInput):
    async def create_customer_by_email_passw(customer):
        if not is_valid_email(customer.email):
            return Error(status=400, message="Email format is invalid!")

        searched_customer = await CustomerModel.find_one({"email": customer.email})
        if searched_customer:
            return Error(status=400, message="Email already in use!")

        if len(customer.password) < 8:
            return Error(
                status=400, message="Password must at least have eight characters!"
            )

        if len(customer.name) < 3:
            return Error(
                status=400, message="Customer name must have at least 3 characters!"
            )

        inserted_customer = await CustomerModel.insert_one(
            CustomerModel(
                name=customer.name,
                email=customer.email,
                password=mybcrypt.hashpw(customer.password),
                fcm_token=customer.fcm_token or None,
                fcm_token_updated_at=datetime.utcnow() if customer.fcm_token else None,
            )
        )
        return await customer_model_to_type(inserted_customer)

    async def create_customer_by_google(customer):
        try:
            id_info = await my_google_auth.verify_id_token(customer.google_id_token)
            searched_customer = await CustomerModel.find_one(
                {"google_id": id_info["sub"]}
            )

            if searched_customer:
                return Error(status="400", message="Google account already in use!")

            inserted_customer = await CustomerModel.insert_one(
                CustomerModel(
                    name=id_info.get("name", None),
                    avatar_url=id_info.get("picture", None),
                    email=id_info["email"],
                    google_id=id_info["sub"],
                    fcm_token=customer.fcm_token or None,
                    fcm_token_updated_at=(
                        datetime.utcnow() if customer.fcm_token else None
                    ),
                )
            )

            return await customer_model_to_type(inserted_customer)

        except ValueError as e:
            print(e)
            return Error(status=400, message="Error verifying Google ID token!")

    async def create_customer_by_apple(customer):
        try:
            id_info = await my_apple_auth.verify_id_token(customer.apple_id_token)
            searched_customer = await CustomerModel.find_one(
                {"apple_id": id_info["sub"]}
            )

            if searched_customer:
                return Error(status="400", message="Apple account already in use!")

            inserted_customer = await CustomerModel.insert_one(
                CustomerModel(
                    name=id_info.get("name", "user"),
                    avatar_url=id_info.get("picture", None),
                    email=id_info["email"],
                    apple_id=id_info["sub"],
                    fcm_token=customer.fcm_token or None,
                    fcm_token_updated_at=(
                        datetime.utcnow() if customer.fcm_token else None
                    ),
                )
            )

            return await customer_model_to_type(inserted_customer)

        except ValueError as e:
            print(e)
            return Error(status=400, message="Error verifying Apple ID token!")

    async def create_customer_by_facebook(customer):
        user_info = await my_fb_auth.verify_access_token(customer.fb_access_token)
        if user_info:
            searched_customer = await CustomerModel.find_one(
                {"facebook_id": user_info["user_id"]}
            )

            if searched_customer:
                return Error(status="400", message="Facebook account already in use!")

            inserted_customer = await CustomerModel.insert_one(
                CustomerModel(
                    name=user_info.get("name", ""),
                    avatar_url=user_info.get("picture", None),
                    email=user_info.get("email", None),
                    facebook_id=user_info["user_id"],
                    fcm_token=customer.fcm_token or None,
                    fcm_token_updated_at=(
                        datetime.utcnow() if customer.fcm_token else None
                    ),
                )
            )

            return await customer_model_to_type(inserted_customer)

        return Error(status=400, message="Error verifying Facebook access token!")

    validator_config = [
        {
            "args": ["name", "email", "password"],
            "handler": create_customer_by_email_passw,
        },
        {
            "args": ["google_id_token"],
            "handler": create_customer_by_google,
        },
        {
            "args": ["apple_id_token"],
            "handler": create_customer_by_apple,
        },
        {
            "args": ["fb_access_token"],
            "handler": create_customer_by_facebook,
        },
    ]

    try:
        return await validate_then_handle(validator_config, customer)

    except ValueError as e:
        return Error(status=400, message=str(e))

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")


async def read_customer_by_jwt(info: Info):
    customer = await get_verified_customer(info)
    if not customer:
        return Error(status=403, message="Forbidden!")

    return await customer_model_to_type(customer)


async def read_customer(customer: CustomerInput):
    async def read_customer_by_email_passw(customer):
        searched_customer = await CustomerModel.find_one(
            {
                "email": customer.email,
                "password": {"$exists": True},
                "deactivated": {"$in": [False, None]},
            }
        )
        if not searched_customer:
            return Error(status=401, message="Invalid email or password!")

        failed_attempts = searched_customer.failed_login_attempts or 0
        if failed_attempts >= 5:
            return Error(status=429, message="Too many failed login attempts!")

        if not mybcrypt.checkpw(customer.password, searched_customer.password):
            await searched_customer.set(
                {
                    CustomerModel.failed_login_attempts: failed_attempts + 1,
                    CustomerModel.latest_failed_login_attempt: datetime.utcnow(),
                }
            )

            return Error(status=401, message="Invalid email or password!")

        if customer.fcm_token:
            searched_customer.fcm_token = customer.fcm_token
            searched_customer.fcm_token_updated_at = datetime.utcnow()
            await searched_customer.save()

        return await customer_model_to_type(searched_customer)

    async def read_customer_by_email_otp(customer):
        searched_customer = await CustomerModel.find_one(
            {
                "email": customer.email,
                "deactivated": {"$in": [False, None]},
            }
        )
        if not searched_customer:
            return Error(status=401, message="Invalid email or OTP!")

        failed_attempts = searched_customer.failed_login_attempts or 0
        if failed_attempts >= 5:
            return Error(status=429, message="Too many failed login attempts!")

        if searched_customer.otp != customer.otp:
            await searched_customer.set(
                {
                    CustomerModel.failed_login_attempts: failed_attempts + 1,
                    CustomerModel.latest_failed_login_attempt: datetime.utcnow(),
                }
            )

            return Error(status=401, message="Invalid email or OTP!")

        if customer.fcm_token:
            searched_customer.fcm_token = customer.fcm_token
            searched_customer.fcm_token_updated_at = datetime.utcnow()
            await searched_customer.save()

        await searched_customer.set(
            {
                CustomerModel.otp: None,
                CustomerModel.otp_created_at: None,
            }
        )

        return await customer_model_to_type(searched_customer)

    async def read_customer_by_google(customer):
        try:
            id_info = await my_google_auth.verify_id_token(customer.google_id_token)
            searched_customer = await CustomerModel.find_one(
                {
                    "google_id": id_info["sub"],
                    "deactivated": {"$in": [False, None]},
                }
            )
            if not searched_customer:
                return Error(
                    status=401,
                    message="No user associated with provided Google account!",
                )

            if customer.fcm_token:
                searched_customer.fcm_token = customer.fcm_token
                searched_customer.fcm_token_updated_at = datetime.utcnow()
                await searched_customer.save()

            return await customer_model_to_type(searched_customer)

        except:
            return Error(status=401, message="Error verifying Google ID token!")

    async def read_customer_by_apple(customer):
        try:
            id_info = await my_apple_auth.verify_id_token(customer.apple_id_token)
            searched_customer = await CustomerModel.find_one(
                {
                    "apple_id": id_info["sub"],
                    "deactivated": {"$in": [False, None]},
                }
            )
            if not searched_customer:
                return Error(
                    status=401,
                    message="No user associated with provided Apple account!",
                )

            if customer.fcm_token:
                searched_customer.fcm_token = customer.fcm_token
                searched_customer.fcm_token_updated_at = datetime.utcnow()
                await searched_customer.save()

            return await customer_model_to_type(searched_customer)

        except:
            return Error(status=401, message="Error verifying Apple ID token!")

    async def read_customer_by_facebook(customer):
        user_info = await my_fb_auth.verify_access_token(customer.fb_access_token)
        if not user_info:
            return Error(status=401, message="Error verifying Facebook access token!")

        searched_customer = await CustomerModel.find_one(
            {
                "facebook_id": user_info["user_id"],
                "deactivated": {"$in": [False, None]},
            }
        )
        if not searched_customer:
            return Error(
                status=401,
                message="No customer associated with provided Facebook account!",
            )

        if customer.fcm_token:
            searched_customer.fcm_token = customer.fcm_token
            searched_customer.fcm_token_updated_at = datetime.utcnow()
            await searched_customer.save()

        return await customer_model_to_type(searched_customer)

    validator_config = [
        {
            "args": ["email", "password"],
            "handler": read_customer_by_email_passw,
        },
        {
            "args": ["email", "password", "fcm_token"],
            "handler": read_customer_by_email_passw,
        },
        {
            "args": ["email", "otp"],
            "handler": read_customer_by_email_otp,
        },
        {
            "args": ["email", "otp", "fcm_token"],
            "handler": read_customer_by_email_otp,
        },
        {
            "args": ["google_id_token"],
            "handler": read_customer_by_google,
        },
        {
            "args": ["google_id_token", "fcm_token"],
            "handler": read_customer_by_google,
        },
        {
            "args": ["apple_id_token"],
            "handler": read_customer_by_apple,
        },
        {
            "args": ["apple_id_token", "fcm_token"],
            "handler": read_customer_by_apple,
        },
        {
            "args": ["fb_access_token"],
            "handler": read_customer_by_facebook,
        },
        {
            "args": ["fb_access_token", "fcm_token"],
            "handler": read_customer_by_facebook,
        },
    ]

    try:
        return await validate_then_handle(validator_config, customer)

    except ValueError as e:
        return Error(status=400, message=str(e))

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")


async def update_customer(customer: UpdateCustomerInput, info: Info):
    try:
        searched_customer = await get_verified_customer(info)
        if not searched_customer:
            return Error(status=403, message="Forbidden")

        if customer.password and len(customer.password) < 8:
            return Error(
                status=400, message="Password must at least have eight characters!"
            )

        if customer.gender and not customer.gender in ["male", "female"]:
            return Error(
                status=400, message='Gender must either be "male" or "female".'
            )

        if customer.profession and not await ProfessionModel.get(customer.profession):
            return Error(status=400, message="Invalid profession ID!")

        existing_events = set(
            [str(n.id) for n in await NotificationEventModel.find_all().to_list()]
        )
        if customer.notification_events and not set(
            customer.notification_events
        ).issubset(existing_events):
            return Error(status=400, message="Invalid event ID!")

        existing_hobbies = set(
            [str(h.id) for h in await HobbyModel.find_all().to_list()]
        )
        if customer.hobbies and not set(customer.hobbies).issubset(existing_hobbies):
            return Error(status=400, message="Invalid hobby ID!")

        existing_sights = set(
            [str(s.id) for s in await SightseeingModel.find_all().to_list()]
        )
        if customer.sightseeing and not set(customer.sightseeing).issubset(
            existing_sights
        ):
            return Error(status=400, message="Invalid sightseeing ID!")

        if customer.password:
            searched_customer.password = mybcrypt.hashpw(customer.password)
            print("##### : ", searched_customer.password)

        if customer.avatar_url:
            searched_customer.avatar_url = customer.avatar_url

        if customer.phone:
            searched_customer.phone = customer.phone

        if customer.gender:
            searched_customer.gender = customer.gender

        if customer.profession:
            searched_customer.profession = customer.profession

        if customer.hobbies:
            searched_customer.hobbies = customer.hobbies

        if customer.sightseeing:
            searched_customer.sightseeing = customer.sightseeing

        if customer.fcm_token:
            searched_customer.fcm_token = customer.fcm_token
            searched_customer.fcm_token_updated_at = datetime.utcnow()

        if customer.notification_events:
            searched_customer.notification_event_ids = customer.notification_events

        if customer.bio:
            searched_customer.bio = customer.bio

        if customer.headline:
            searched_customer.headline = customer.headline

        if customer.address:
            coords = await my_gmaps.find_place_coordinates(customer.address)
            if coords:
                searched_customer.address_latitude = coords[0]
                searched_customer.address_longitude = coords[1]

            searched_customer.address = customer.address

        if customer.append_contacts:
            searched_customer.contacts = set(
                [*(searched_customer.contacts or []), *customer.append_contacts]
            )

        if customer.description:
            searched_customer.description = customer.description

        if customer.name:
            searched_customer.name = customer.name

        if customer.email:
            searched_customer.email = customer.email

        if customer.language_country_iso_code:
            [language_code, country_code] = customer.language_country_iso_code.split(
                "-"
            )
            language = language_name(language_code)
            country = countries.get(alpha_2=country_code)
            if not (language and country):
                return Error(
                    status=400, message="Invalid value for currency_country_iso_code!"
                )

            searched_customer.language_country_iso_code = (
                customer.language_country_iso_code.upper()
            )

        if customer.currency_country_iso_code:
            [currency_code, country_code] = customer.currency_country_iso_code.split(
                "-"
            )
            currency = numbers.get_currency_name(currency_code)
            country = countries.get(alpha_2=country_code)
            if not country or currency == currency_code:
                return Error(
                    status=400, message="Invalid value for currency_country_iso_code!"
                )

            searched_customer.currency_country_iso_code = (
                customer.currency_country_iso_code
            )

        if customer.travelling_unit_code:
            if not customer.travelling_unit_code in travelling_units.keys():
                return Error(
                    status=400, message="Invalid value for travelling_unit_code!"
                )

            searched_customer.travelling_unit_code = customer.travelling_unit_code

        if getattr(customer, "is_private", None):
            searched_customer.is_private = getattr(customer, "is_private")
        else:
            searched_customer.is_private = False

        searched_customer.updated_at = datetime.now(timezone.utc)

        await searched_customer.save()

        return await customer_model_to_type(searched_customer)

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")


async def delete_customer(customer: DeleteCustomerInput, info: Info):
    try:
        verified_customer = await get_verified_customer(info)
        if not verified_customer:
            return Error(status=403, message="Forbidden!")

        if customer.permanent:
            verified_customer.permanently_deactivated = True

        verified_customer.deactivated = True
        verified_customer.updated_at = datetime.now(timezone.utc)
        await verified_customer.save()

        return Error(status=200, message="Customer deleted successfully!")

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")


async def create_customer_otp(otp: CreateOtpInput):
    code = "".join([str(random.randint(0, 9)) for i in range(0, 6)])

    async def create_email_otp(customer):
        if is_valid_email(customer.email):
            searched_customer = await CustomerModel.find_one({"email": customer.email})
            if not searched_customer:
                return Error(
                    status=404, message="No customer registered with provided email!"
                )

            await searched_customer.set(
                {
                    CustomerModel.otp: code,
                    CustomerModel.otp_created_at: datetime.utcnow(),
                }
            )
            await mysmtp.send_otp_email(code, customer.email)

            return Error(status=201, message="Customer OTP created successfully!")

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


async def read_all_customers(customers: AllCustomersInput, info: Info):
    try:
        verified_admin = await get_verified_gl_admin(info)
        if not verified_admin:
            return Error(status=403, message="Forbidden!")

        if customers.page is None:
            customers.page = 1

        if (
            len(
                [
                    f
                    for f in [
                        customers.active_users,
                        customers.content_users,
                        customers.enterprise_users,
                    ]
                    if f
                ]
            )
            > 1
        ):
            return Error(status=400, message="Only one of these filters is required.")

        query = (
            CustomerModel.find()
            .limit(config.PAGE_SIZE)
            .skip((customers.page - 1) * config.PAGE_SIZE)
        )
        if customers.active_users:
            query = CustomerModel.find(
                {
                    "$or": [
                        {"permanently_deactivated": False},
                        {"permanently_deactivated": {"$exists": False}},
                    ]
                }
            )

        if customers.content_users:
            # query = query.find(CustomerModel.content_user == True)
            return Error(status=501, message="Content users support is coming soon!")

        if customers.enterprise_users:
            # query = query.find(CustomerModel.enterprise_user == True)
            return Error(status=501, message="Enterprise users support is coming soon!")

        total_records = await query.count()
        query = await query.to_list()
        return AllCustomersPage(
            items=[await customer_model_to_type(n) for n in query],
            page=customers.page,
            total=total_records,
        )
    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")
