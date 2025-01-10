from lib import utils
from lib.constants import support_inquiry_types
from lib.graphql.inputs.create_support_inquiry_input import CreateSupportInquiryInput
from lib.graphql.types.error import Error
from lib.graphql.types.tag import Tag
from lib.graphql.types.tag_page import TagPage
from lib.models.support_inquiry import SupportInquiry


def read_support_inquiry_types():
    try:
        return TagPage(
            items=[Tag(id=k, label=v) for k, v in support_inquiry_types.items.items()],
            page=1,
            total=len(support_inquiry_types.items.items()),
        )

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")


async def create_support_inquiry(inquiry: CreateSupportInquiryInput):
    try:
        inquiry_type = support_inquiry_types.items[inquiry.type]

        if not utils.is_valid_email(inquiry.email):
            return Error(status=400, message="Invalid email format!")

        if not inquiry_type:
            return Error(status=400, message="Invalid inquiry type ID!")

        await SupportInquiry.insert_one(
            SupportInquiry(
                name=inquiry.name,
                email=inquiry.email,
                type_id=inquiry.type,
                subject=inquiry.subject,
                description=inquiry.description,
            )
        )

        return Error(status=200, message="Support inquiry created successfully")

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")
