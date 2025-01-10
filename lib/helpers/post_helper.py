from lib.graphql.types.post import Post
from lib.models.post_model import PostModel


async def post_model_to_type(model: PostModel):
    return Post(
        id=model.id,
        shared_w_friends=model.shared_w_friends or False,
        title=model.title,
        image_url=model.image_url,
        video_url=model.video_url,
        map_url=model.map_url,
        social_platform=model.social_platform,
    )
