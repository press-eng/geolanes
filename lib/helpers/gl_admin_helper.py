from typing import Optional

from beanie import PydanticObjectId
from beanie.operators import In
from strawberry.types import Info

from lib.graphql.types.gl_admin import GlAdmin
from lib.graphql.types.gl_admin_public import GlAdminPublic
from lib.models.gl_admin_model import GlAdminModel
from lib.services import myjwt


async def gl_admin_model_to_type(model: GlAdminModel) -> GlAdmin:

    return GlAdmin(
        id=str(model.id),
        name=model.name,
        jwt=myjwt.encode({"glAdminId": str(model.id)}),
        email=model.email,
        phone=model.phone,
        gender=model.gender,
        avatar_url=model.avatar_url,
        address=model.address,
    )


async def get_verified_gl_admin(info: Info) -> Optional[GlAdminModel]:
    auth_header = info.context["request"].headers.get("Authorization") or ""
    token = auth_header[len("Bearer ") :]
    if token:
        try:
            json = myjwt.decode(token)
            searched_admin = await GlAdminModel.find(
                GlAdminModel.id == PydanticObjectId(json["glAdminId"]),
                In(GlAdminModel.deactivated, [False, None]),
            ).first_or_none()
            if searched_admin:
                return searched_admin

        except:
            pass

    return None


def gl_admin_model_to_public_type(model: GlAdminModel) -> GlAdminPublic:
    return GlAdminPublic(
        id=model.id,
        name=model.name,
        avatar_url=model.avatar_url,
    )
