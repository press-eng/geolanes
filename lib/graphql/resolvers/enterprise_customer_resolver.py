from datetime import datetime, timezone

import strawberry
from beanie import PydanticObjectId
from fastapi import Request
from strawberry.types import Info

from lib import config
from lib.graphql.inputs import enterprise_customer_input
from lib.graphql.types.enterprise_customer import (
    EnterpriseCustomerResponse,
    PaginatedEntCustomerList,
)
from lib.graphql.types.error import Error
from lib.helpers import email_helper
from lib.helpers.enterprise_customer_helper import (
    ent_customer_model_to_type,
    export_ent_customer_to_csv,
    export_ent_customer_to_pdf,
)
from lib.helpers.gl_admin_helper import get_verified_gl_admin
from lib.models.enterprise_customer_model import EnterpriseCustomerModel
from lib.models.other_contact_model import OtherContact
from lib.services import mybcrypt, myjwt
from lib.utils import is_valid_email


async def create_enterprise_customer(
    self, input: enterprise_customer_input.CreateEnterpriseCustomerInput, info: Info
):

    # Access the Request object from the context
    request: Request = info.context["request"]

    verified_admin = await get_verified_gl_admin(info)
    if not verified_admin:
        return Error(status=403, message="Forbidden!")

    if not is_valid_email(input.email):
        return Error(status=400, message="Email format is invalid!")

    searched_customer = await EnterpriseCustomerModel.find_one({"email": input.email})
    if searched_customer:
        return Error(status=400, message="Email already in use!")

    ent_customer = EnterpriseCustomerModel(
        name=input.name,
        email=input.email,
        other_contact_info={
            "name": input.other_contact_name,
            "contact_number": input.other_contact_number,
        },
        customer_status="Active",
        customer_id=input.customer_id,
        role=input.role,
        price_plan=input.price_plan,
        country_state=input.country_state,
        avatar_url=input.avatar_url,
    )
    new_customer = await ent_customer.insert()

    new_customer_id = new_customer.id
    new_customer_email = new_customer.email

    # jwt = myjwt.encode({"id": str(new_customer_id)})

    base_url = f"{request.url.scheme}://{request.url.hostname}:{request.url.port}/"

    reset_link = f"{base_url}customer/{new_customer_id}"
    print("Signup Email sending....")

    # commented beacause SMTP server not working
    # vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
    # email_helper.send_email_with_template(
    #     config.SMTP_SERVER,
    #     config.SMTP_PORT,
    #     config.SMTP_SENDER_EMAIL,
    #     new_customer_email,
    #     reset_link,
    # )

    return EnterpriseCustomerResponse(
        status=201,
        message="Customer registered successfully!",
        customer=await ent_customer_model_to_type(new_customer),
    )


async def update_enterprise_customer(
    self, input: enterprise_customer_input.UpdateEnterpriseCustomerInput, info: Info
):
    verified_admin = await get_verified_gl_admin(info)
    if not verified_admin:
        return Error(status=403, message="Forbidden!")

    if not input.id:
        return Error(status=400, message="Missing required data")

    searched_customer = await EnterpriseCustomerModel.find_one(
        {"_id": PydanticObjectId(input.id)}
    )
    if not searched_customer:
        return Error(status=400, message="Invalid ID")

    if input.is_deleted == True:
        searched_customer.is_deleted = True
        searched_customer.deleted_at = datetime.now(timezone.utc)
    else:
        if input.name is not None:
            searched_customer.name = input.name
        if input.avatar_url is not None:
            searched_customer.avatar_url = input.avatar_url
        if input.role is not None:
            searched_customer.role = input.role
        if input.price_plan is not None:
            searched_customer.price_plan = input.price_plan
        if input.country_state is not None:
            searched_customer.country_state = input.country_state

        if input.other_contact_name or input.other_contact_number:
            searched_customer.other_contact_info = {
                "name": input.other_contact_name
                or searched_customer.other_contact_info.get("name"),
                "contact_number": input.other_contact_number
                or searched_customer.other_contact_info.get("contact_number"),
            }

        if input.customer_status:
            searched_customer.customer_status = input.customer_status

        searched_customer.updated_at = datetime.now(timezone.utc)

    updated_customer = await searched_customer.save()

    return EnterpriseCustomerResponse(
        status=200,
        message="Customer updated successfully!",
        customer=await ent_customer_model_to_type(updated_customer),
    )


async def get_enterprise_customers(
    self, input: enterprise_customer_input.entCustomerPaginationInput, info: Info
):

    verified_admin = await get_verified_gl_admin(info)
    if not verified_admin:
        return Error(status=403, message="Forbidden!")

    print("all ent_customers with filters")

    page = input.page

    page_size = config.PAGE_SIZE

    filter = {}

    if input.id:
        customer_data = await EnterpriseCustomerModel.find_one(
            {"_id": PydanticObjectId(input.id)}
        )
        if not customer_data:
            return Error(status=400, message="Customer not exist!")
        else:
            return EnterpriseCustomerResponse(
                status=200,
                message="Customer found!",
                customer=await ent_customer_model_to_type(customer_data),
            )

    else:
        if input.search_text:
            filter["name"] = {"$regex": input.search_text, "$options": "i"}

        if input.customer_status:
            if input.customer_status == "Active" or input.customer_status == "Inactive":
                filter["customer_status"] = {
                    "$regex": input.customer_status,
                    "$options": "i",
                }

        if input.date:
            given_datetime = datetime.strptime(input.date, "%Y-%m-%d")

            start_date = given_datetime.replace(
                hour=0, minute=0, second=0, microsecond=0, tzinfo=timezone.utc
            )
            end_date = given_datetime.replace(
                hour=23, minute=59, second=59, microsecond=999999, tzinfo=timezone.utc
            )
            filter["created_at"] = {"$gte": start_date, "$lte": end_date}

        filter["is_deleted"] = False

        print("filters : ", filter)

        customers = (
            await EnterpriseCustomerModel.find(filter)
            .skip((page - 1) * page_size)
            .limit(page_size)
            .to_list()
        )
        customer_arr = []
        for customer in customers:
            customer_arr.append(ent_customer_model_to_type(customer))
        total_count = await EnterpriseCustomerModel.find(filter).count()

        current_datetime = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        if input.export_type == "pdf":
            export_customers = await EnterpriseCustomerModel.find(filter).to_list()
            # export pdf
            pdf_file_name = "ent_customer_" + current_datetime + ".pdf"
            await export_ent_customer_to_pdf(export_customers, pdf_file_name)
            print(
                f"Enterprise customers data exported to {pdf_file_name} successfully!"
            )
            pdf_download_path = f"/exports/pdf/{pdf_file_name}"
            return Error(status=200, message=pdf_download_path)

        if input.export_type == "csv":
            export_customers = await EnterpriseCustomerModel.find(filter).to_list()
            # csv export
            csv_file_name = "ent_customer_" + current_datetime + ".csv"
            await export_ent_customer_to_csv(export_customers, csv_file_name)
            print(
                f"Enterprise customers data exported to {csv_file_name} successfully!"
            )
            csv_download_path = f"/exports/csv/{csv_file_name}"
            return Error(status=200, message=csv_download_path)

        return PaginatedEntCustomerList(
            status=200,
            message="Success",
            page=page,
            total_count=total_count,
            data=customer_arr,
        )


async def ent_customer_bulk_operations(
    self, input: enterprise_customer_input.customerBulkOperationInput, info: Info
):

    verified_admin = await get_verified_gl_admin(info)
    if not verified_admin:
        return Error(status=403, message="Forbidden!")

    if input.ids and input.operation:
        if input.operation == "Delete" or input.operation == "delete":
            print("bulk operation : delete")
            for campaign_id in input.ids:
                customer_data = await EnterpriseCustomerModel.find_one(
                    EnterpriseCustomerModel.id == PydanticObjectId(campaign_id)
                )
                customer_data.is_deleted = True
                customer_data.deleted_at = datetime.now(timezone.utc)
                customer_data.updated_at = datetime.now(timezone.utc)
                await customer_data.save()

            return Error(status=200, message="Deleted successfully")

        elif input.operation == "Active" or input.operation == "active":
            print("bulk operation : customer_status")
            for campaign_id in input.ids:
                customer_data = await EnterpriseCustomerModel.find_one(
                    EnterpriseCustomerModel.id == PydanticObjectId(campaign_id)
                )
                customer_data.customer_status = "Active"

                customer_data.updated_at = datetime.now(timezone.utc)
                await customer_data.save()

            return Error(status=200, message="Actived successfully")

        elif input.operation == "Inactive" or input.operation == "inactive":
            print("bulk operation : customer_status")
            for campaign_id in input.ids:
                customer_data = await EnterpriseCustomerModel.find_one(
                    EnterpriseCustomerModel.id == PydanticObjectId(campaign_id)
                )
                customer_data.customer_status = "Inactive"

                customer_data.updated_at = datetime.now(timezone.utc)
                await customer_data.save()

            return Error(status=200, message="Deactived successfully")

        else:
            return Error(status=500, message="Something went wrong!")

    return Error(status=400, message="missing required fileds")


async def update_enterprise_customer_password(
    self, input: enterprise_customer_input.UpdateEnterpriseCustomerPasswordInput
):

    if not input.id or not input.password:
        return Error(status=400, message="Missing required data")

    searched_customer = await EnterpriseCustomerModel.find_one(
        {"_id": PydanticObjectId(input.id)}
    )
    if not searched_customer:
        return Error(status=400, message="Invalid ID")

    searched_customer.password = mybcrypt.hashpw(input.password)
    searched_customer.updated_at = datetime.now(timezone.utc)

    await searched_customer.save()

    return Error(
        status=200,
        message="Password update successfully!",
    )
