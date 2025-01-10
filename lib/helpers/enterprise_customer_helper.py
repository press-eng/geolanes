import csv
from datetime import datetime
from typing import List

import pandas as pd
import strawberry
from beanie import PydanticObjectId
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from lib.graphql.types.enterprise_customer import EnterpriseCustomer, OtherContact
from lib.models.enterprise_customer_model import EnterpriseCustomerModel


async def ent_customer_model_to_type(
    model: EnterpriseCustomerModel,
):

    other_contact_info_instance = (
        OtherContact(
            **model.other_contact_info) if model.other_contact_info else None
    )

    return EnterpriseCustomer(
        id=strawberry.ID(str(model.id)),
        name=model.name,
        email=model.email,
        avatar_url=model.avatar_url,
        customer_id=model.customer_id,
        role=model.role,
        customer_status=model.customer_status,
        price_plan=model.price_plan,
        country_state=model.country_state,
        account_type=model.account_type,
        other_contact_info=other_contact_info_instance,
        is_deleted=model.is_deleted,
        deleted_at=model.deleted_at,
        updated_at=model.updated_at,
        created_at=model.created_at,
    )


async def export_ent_customer_to_pdf(customers, file_name):
    c = canvas.Canvas(f"exports/pdf/{file_name}", pagesize=landscape(A4))
    today_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    # Add title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100 * mm, 200 * mm, "Enterprise Customers Data")

    c.setFont("Helvetica-Bold", 8)
    c.drawString(118 * mm, 195 * mm, f"Date : {today_date}")

    # Add table headers
    c.setFont("Helvetica-Bold", 12)
    c.drawString(10 * mm, 185 * mm, "Name")
    c.drawString(45 * mm, 185 * mm, "Country/State")
    c.drawString(80 * mm, 185 * mm, "Role")
    c.drawString(100 * mm, 185 * mm, "Price Plan")
    c.drawString(128 * mm, 185 * mm, "Email")
    c.drawString(178 * mm, 185 * mm, "Status")
    c.drawString(205 * mm, 185 * mm, "Contact Info")

    # Draw the table rows
    c.setFont("Helvetica", 10)
    y_position = 175 * mm  # Initial vertical position for the first row

    # Data
    for customer in customers:

        # Define font size for each cell
        c.setFont("Helvetica", 8)
        c.drawString(10 * mm, y_position, str(customer.name))

        c.setFont("Helvetica", 8)
        c.drawString(45 * mm, y_position, str(customer.country_state))

        c.setFont("Helvetica", 8)
        c.drawString(80 * mm, y_position, str(customer.role))

        c.setFont("Helvetica", 8)
        c.drawString(100 * mm, y_position, str(customer.price_plan))

        c.setFont("Helvetica-Bold", 8)
        c.drawString(128 * mm, y_position, str(customer.email))

        c.setFont("Helvetica", 8)
        c.drawString(178 * mm, y_position, str(customer.customer_status))

        c.setFont("Helvetica", 10)
        c.drawString(
            205 * mm,
            y_position,
            f"{customer.other_contact_info.get('name')}, {customer.other_contact_info.get('contact_number')}",
        )

        y_position -= 10 * mm  # Move down for the next row

    c.save()


async def export_ent_customer_to_csv(customers, file_name):

    extracted_data = []
    for customer in customers:

        campaign_dict = {
            "name": customer.name,
            "email": customer.email,
            "contact info": customer.other_contact_info.get("name")
            + " "
            + customer.other_contact_info.get("contact_number"),
            "customer_id": customer.customer_id,
            "role": customer.role,
            "price_plan": customer.price_plan,
            "country_state": customer.country_state,
            "customer_status": customer.customer_status,
        }
        extracted_data.append(campaign_dict)

    # Convert extracted data into DataFrame
    df = pd.DataFrame(extracted_data)

    df.to_csv(f"exports/csv/{file_name}", index=False)
