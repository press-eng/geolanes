from typing import Optional

import strawberry


@strawberry.type
class Post:
    id: strawberry.ID
    shared_w_friends: bool
    title: Optional[str] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    map_url: Optional[str] = None
    social_platform: Optional[str] = None
