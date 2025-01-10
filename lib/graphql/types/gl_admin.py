from typing import List, Optional

import strawberry


@strawberry.type
class GlAdmin:
    id: str
    name: str
    jwt: str
    email: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    avatar_url: Optional[str] = None
    address: Optional[str] = None
