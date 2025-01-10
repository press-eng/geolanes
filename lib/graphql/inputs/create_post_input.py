from typing import Optional

import strawberry


@strawberry.input
class CreatePostInput:
    title: Optional[str] = strawberry.UNSET
    image_url: Optional[str] = strawberry.UNSET
    video_url: Optional[str] = strawberry.UNSET
    map_url: Optional[str] = strawberry.UNSET
    shared_w_friends: Optional[bool] = strawberry.UNSET
    social_platform: Optional[str] = strawberry.UNSET
