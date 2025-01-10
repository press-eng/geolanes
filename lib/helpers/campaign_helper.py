from datetime import datetime, timezone

import pandas as pd
from beanie import PydanticObjectId
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from lib.graphql.types.campaign import Campaign
from lib.helpers.general_helper import shorten_description
from lib.models.campaign_model import CampaignModel


async def campaign_model_to_type(model: CampaignModel) -> Campaign:
    return Campaign(
        id=str(model.id),
        campaign_name=model.campaign_name,
        target_audience=model.target_audience,
        description=model.description,
        start_date=model.start_date,
        end_date=model.end_date,
        publish_status=model.publish_status,
        active_status=model.active_status,
        impressions_count=model.impressions_count,
        clicks_count=model.clicks_count,
        earning=model.earning,
        campaign_type=model.campaign_type,
        updated_at=model.updated_at,
        created_at=model.created_at,
        image_urls=model.image_urls,
        video_urls=model.video_urls,
        audio_urls=model.audio_urls,
        is_deleted=model.is_deleted,
        deleted_at=model.deleted_at,
        customer_ref=model.customer_ref,
    )


def export_campaigns_to_csv(campaigns, file_name):
    extracted_data = []
    for campaign in campaigns:

        if campaign.publish_status == False:
            p_status = "No"
        elif campaign.publish_status == True:
            p_status = "Yes"
        else:
            p_status = str(campaign.publish_status)

        if campaign.active_status == False:
            a_status = "No"
        elif campaign.active_status == True:
            a_status = "Yes"
        else:
            a_status = str(campaign.active_status)

        if campaign.image_urls:
            images = ", ".join(campaign.image_urls)
        else:
            images = "N/A"

        if campaign.video_urls:
            videos = ", ".join(campaign.video_urls)
        else:
            videos = "N/A"

        if campaign.audio_urls:
            audios = ", ".join(campaign.audio_urls)
        else:
            audios = "N/A"

        campaign_dict = {
            "campaign_name": campaign.campaign_name,
            "description": (
                campaign.description if campaign.description else "No description"
            ),
            "target_audience": campaign.target_audience,
            "type": campaign.campaign_type,
            "start_date": campaign.start_date,
            "end_date": campaign.end_date,
            "publish": p_status,
            "active": a_status,
            "image_urls": images,
            "video_urls": videos,
            "audio_urls": audios,
            "impressions_count": campaign.impressions_count,
            "clicks_count": campaign.clicks_count,
            "earning": campaign.earning,
        }
        extracted_data.append(campaign_dict)

    # Convert extracted data into DataFrame
    df = pd.DataFrame(extracted_data)

    df.to_csv(f"exports/csv/{file_name}", index=False)


def export_campaigns_to_pdf(campaigns, file_name):
    c = canvas.Canvas(f"exports/pdf/{file_name}", pagesize=landscape(A4))
    today_date = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    # Add title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(115 * mm, 200 * mm, "Campaign Data")

    c.setFont("Helvetica-Bold", 8)
    c.drawString(118 * mm, 195 * mm, f"Date : {today_date}")

    # Add table headers
    c.setFont("Helvetica-Bold", 12)
    c.drawString(10 * mm, 185 * mm, "Name")
    c.drawString(35 * mm, 185 * mm, "Description")
    c.drawString(78 * mm, 185 * mm, "Type")
    c.drawString(95 * mm, 185 * mm, "Audience")
    c.drawString(118 * mm, 185 * mm, "Start Date")
    c.drawString(153 * mm, 185 * mm, "End Date")
    c.drawString(190 * mm, 185 * mm, "Publish")
    c.drawString(208 * mm, 185 * mm, "Active")
    c.drawString(225 * mm, 185 * mm, "Imp.")
    c.drawString(238 * mm, 185 * mm, "Clicks")
    c.drawString(255 * mm, 185 * mm, "Earning($)")

    # Draw the table rows
    c.setFont("Helvetica", 10)
    y_position = 175 * mm  # Initial vertical position for the first row

    # Data
    for campaign in campaigns:

        c_type = "".join([word[0].upper() for word in campaign.campaign_type.split()])

        if " " in campaign.target_audience:
            audience = "".join(
                [word[0].upper() for word in campaign.target_audience.split()]
            )
        else:
            audience = campaign.target_audience.upper()

        description = shorten_description(str(campaign.description))

        if campaign.publish_status == False:
            p_status = "No"
        elif campaign.publish_status == True:
            p_status = "Yes"
        else:
            p_status = str(campaign.publish_status)

        if campaign.active_status == False:
            a_status = "No"
        elif campaign.active_status == True:
            a_status = "Yes"
        else:
            a_status = str(campaign.active_status)

        # Define font size for each cell
        c.setFont("Helvetica", 8)
        c.drawString(10 * mm, y_position, str(campaign.campaign_name))

        c.setFont("Helvetica", 8)
        c.drawString(35 * mm, y_position, str(description))

        c.setFont("Helvetica", 8)
        c.drawString(78 * mm, y_position, str(c_type))
        c.drawString(95 * mm, y_position, str(audience))

        c.setFont("Helvetica", 8)
        c.drawString(118 * mm, y_position, str(campaign.start_date))
        c.drawString(153 * mm, y_position, str(campaign.end_date))

        c.setFont("Helvetica-Bold", 8)
        c.drawString(195 * mm, y_position, str(p_status))
        c.drawString(213 * mm, y_position, str(a_status))

        c.setFont("Helvetica", 8)
        c.drawString(225 * mm, y_position, str(campaign.impressions_count))
        c.drawString(238 * mm, y_position, str(campaign.clicks_count))

        c.setFont("Helvetica", 10)
        c.drawString(255 * mm, y_position, f"{str(campaign.earning)} $")

        y_position -= 10 * mm  # Move down for the next row

    c.save()


async def publish_campaign(campaign_id):

    campaign_data = await CampaignModel.find(
        CampaignModel.id == PydanticObjectId(campaign_id),
        CampaignModel.publish_status == False,
        CampaignModel.is_deleted == False,
    ).first_or_none()
    campaign_data.publish_status = True
    campaign_data.active_status = True
    campaign_data.published_at = datetime.utcnow()

    campaign_data.updated_at = datetime.now(timezone.utc)

    await campaign_data.save()

    print(f"Campaign {campaign_id} published successfully.")


async def check_and_publish_campaigns():
    print("campaign publisher")
    now = datetime.utcnow()
    print(f"Checking campaigns at: {now}")

    campaigns_to_publish = await CampaignModel.find(
        {
            "start_date": {"$lte": now},
            "publish_status": False,
            "is_deleted": False,  # not published
        }
    ).to_list()

    for camp in campaigns_to_publish:
        campaign_id = camp.id
        await publish_campaign(campaign_id)


async def unpublish_campaign(campaign_id):

    campaign_data = await CampaignModel.find(
        CampaignModel.id == PydanticObjectId(campaign_id),
        CampaignModel.publish_status == True,
        CampaignModel.active_status == True,
        CampaignModel.is_deleted == False,
    ).first_or_none()
    campaign_data.publish_status = True
    campaign_data.active_status = False

    campaign_data.updated_at = datetime.now(timezone.utc)

    await campaign_data.save()

    print(f"Campaign {campaign_id} stop published successfully.")


async def check_and_unpublish_campaigns():
    print("campaign unpublisher")
    now = datetime.utcnow()
    print(f"Checking campaigns at: {now}")

    campaigns_to_publish = await CampaignModel.find(
        {
            "end_date": {"$lte": now},
            "publish_status": True,
            "active_status": True,
            "is_deleted": False,
        }
    ).to_list()

    for camp in campaigns_to_publish:
        campaign_id = camp.id
        await unpublish_campaign(campaign_id)
