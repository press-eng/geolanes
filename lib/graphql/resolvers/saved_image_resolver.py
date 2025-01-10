from beanie import PydanticObjectId
from strawberry.types import Info

from lib import config, utils
from lib.graphql.inputs.create_saved_image_input import CreateSavedImageInput
from lib.graphql.inputs.delete_saved_image_input import DeleteSavedImageinput
from lib.graphql.inputs.saved_image_input import SavedImageInput
from lib.graphql.types.error import Error
from lib.graphql.types.saved_image import SavedImage
from lib.graphql.types.saved_image_page import SavedImagePage
from lib.helpers.customer_helper import get_verified_customer
from lib.models.saved_image_model import SavedImageModel


async def create_saved_image(image: CreateSavedImageInput, info: Info):
    try:
        customer = await get_verified_customer(info)
        if not customer:
            return Error(status=403, message="Forbidden!")

        await SavedImageModel.insert_one(
            SavedImageModel(image_url=image.image, customer_id=str(customer.id))
        )

        return Error(status=201, message="Saved image created successfully!")

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")


async def read_saved_image_page(image: SavedImageInput, info: Info):
    page = image.page or 1

    try:
        customer = await get_verified_customer(info)
        if not customer:
            return Error(status=403, message="Forbidden!")

        query = (
            SavedImageModel.find(SavedImageModel.customer_id == str(customer.id))
            .skip(config.PAGE_SIZE * (page - 1))
            .limit(config.PAGE_SIZE)
        )
        searched_images = await query.to_list()

        return SavedImagePage(
            items=[
                SavedImage(
                    id=str(i.id), image=i.image_url, created_at=i.id.generation_time
                )
                for i in searched_images
            ],
            page=page,
            total=await query.count(),
        )

    except Exception as e:
        print(e)
        return Error(status=500, message="Something went wrong!")


def delete_saved_image(image: DeleteSavedImageinput, info: Info):
    return utils.create_delete_resolver(
        id=image.id,
        roles=["customer"],
        Model=SavedImageModel,
        success_message="Saved image deleted successfully!",
        info=info,
    )
