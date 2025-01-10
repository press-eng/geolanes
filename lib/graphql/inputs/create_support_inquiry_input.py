import strawberry


@strawberry.input
class CreateSupportInquiryInput:
    name: str
    email: str
    type: strawberry.ID
    subject: str
    description: str
