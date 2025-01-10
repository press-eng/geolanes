from typing import Optional

import strawberry


@strawberry.input
class DeleteCustomerSightseeingInput:
    sightseeing_id: Optional[strawberry.ID] = strawberry.UNSET
