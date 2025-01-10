from typing import Optional

import strawberry


@strawberry.input
class PackageInput:
    page: Optional[int] = strawberry.UNSET
