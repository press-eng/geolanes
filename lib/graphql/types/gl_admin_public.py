from typing import Optional

import strawberry


@strawberry.type
class GlAdminPublic:
    id: str
    name: str
    avatar_url: Optional[str] = None
