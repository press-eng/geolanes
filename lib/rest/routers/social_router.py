import jinja2
from beanie import PydanticObjectId
from fastapi import HTTPException
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter

from lib.models.customer_model import CustomerModel
from lib.models.post_model import PostModel

router = APIRouter()

jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader("assets/templates"))


@router.get("/{id}", include_in_schema=False)
@router.get("/{id}/", response_class=HTMLResponse)
async def get_post(id: str):
    post = await PostModel.get(PydanticObjectId(id))
    if not post:
        return HTTPException(status_code=404, detail="Not Found!")

    customer = await CustomerModel.get(PydanticObjectId(post.customer_id))

    template = jinja_env.get_template("social-post.html")
    output = template.render(
        post={
            "id": str(post.id),
            "image": post.image_url,
            "customer": customer.name,
        }
    )
    return HTMLResponse(
        output,
        headers={
            "Cache-Control": "public, max-age=0, must-revalidate",
        },
    )
