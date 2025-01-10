from typing import Optional

import strawberry


@strawberry.input
class UpdatePostInput:
    id: strawberry.ID
    title: Optional[str] = strawberry.UNSET
    image_url: Optional[str] = strawberry.UNSET
    video_url: Optional[str] = strawberry.UNSET
    map_url: Optional[str] = strawberry.UNSET
    social_platform: Optional[str] = strawberry.UNSET
