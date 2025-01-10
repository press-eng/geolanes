from datetime import datetime, timezone

from beanie import PydanticObjectId
from strawberry.types import Info

from lib import config
from lib.graphql.inputs.create_post_input import CreatePostInput
from lib.graphql.inputs.post_input import PostInput
from lib.graphql.inputs.update_post_input import UpdatePostInput
from lib.graphql.types.error import Error
from lib.graphql.types.post_page import PostPage
from lib.helpers.customer_helper import get_verified_customer
from lib.helpers.gl_admin_helper import get_verified_gl_admin
from lib.helpers.post_helper import post_model_to_type
from lib.models.post_model import PostModel


async def read_posts(posts: PostInput, info: Info):
    page = posts.page or 1
    try:
        customer = await get_verified_customer(info)
        admin = await get_verified_gl_admin(info)
        if not customer and not admin:
            return Error(status=403, message="Forbidden!")

        query = (
            PostModel.find().limit(config.PAGE_SIZE).skip((page - 1) * config.PAGE_SIZE)
        )

        if customer:
            query = query.find(PostModel.customer_id == str(customer.id))
        if admin:
            if posts.customer_id:
                query = query.find(PostModel.customer_id == posts.customer_id)

        if posts.id:
            query = query.find(PostModel.id == PydanticObjectId(posts.id))

        if posts.shared_w_friends or posts.shared_w_friends == False:
            query = query.find(PostModel.shared_w_friends == posts.shared_w_friends)

        if posts.shared_on_social:
            query = query.find({PostModel.social_platform: {"$ne": None}})

        if posts.shared_on_social == False:
            query = query.find(PostModel.social_platform == None)

        records = await query.to_list()
        total_records = await query.count()

        return PostPage(
            items=[await post_model_to_type(p) for p in records],
            page=page,
            total=total_records,
        )

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")


async def create_post(post: CreatePostInput, info: Info):
    try:
        customer = await get_verified_customer(info)
        if not customer:
            return Error(status=403, message="Forbidden!")

        inserted_post = await PostModel.insert_one(
            PostModel(
                customer_id=str(customer.id),
                title=post.title or None,
                image_url=post.image_url or None,
                video_url=post.video_url or None,
                map_url=post.map_url or None,
                shared_w_friends=post.shared_w_friends or None,
                social_platform=post.social_platform or None,
            )
        )

        return await post_model_to_type(inserted_post)

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")


async def update_post(post: UpdatePostInput, info: Info):
    try:
        customer = await get_verified_customer(info)
        if not customer:
            return Error(status=403, message="Forbidden!")

        searched_post = await PostModel.find(
            PostModel.customer_id == str(customer.id),
            PostModel.id == PydanticObjectId(post.id),
        ).first_or_none()
        if not post:
            return Error(status=404, message="Not Found!")

        if post.title:
            searched_post.title = post.title

        if post.image_url:
            searched_post.image_url = post.image_url

        if post.video_url:
            searched_post.video_url = post.video_url

        if post.map_url:
            searched_post.map_url = post.map_url

        if post.social_platform:
            searched_post.social_platform = post.social_platform

        searched_post.updated_at = datetime.now(timezone.utc)
        await searched_post.save()

        return await post_model_to_type(post)

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")
