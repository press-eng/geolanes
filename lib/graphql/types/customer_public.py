from typing import Optional

import strawberry


@strawberry.type
class CustomerPublic:
    id: str
    name: str
    email: Optional[str] = None
    avatar_url: Optional[str] = None
