import strawberry


@strawberry.input
class CreateFollowedCustomerInput:
    customer: strawberry.ID
