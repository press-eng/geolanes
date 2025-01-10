from typing import Optional

import strawberry


@strawberry.input
class DeleteCustomerInput:
    permanent: Optional[bool] = strawberry.UNSET
