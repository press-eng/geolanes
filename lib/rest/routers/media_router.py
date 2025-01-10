import os
import pathlib
import shutil
import uuid

from fastapi import UploadFile
from fastapi.routing import APIRouter

from lib.rest.responses.media_response import MediaResponse

router = APIRouter()

MEDIA_ROUTE = "/media"


@router.post("/", include_in_schema=False)
@router.post("", response_model=MediaResponse, deprecated=True)
async def create_upload_file(file: UploadFile):
    upload_dir = os.path.join(os.getcwd(), "uploads")
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    random_file_name = str(uuid.uuid4())
    file_extension = pathlib.Path(file.filename).suffix
    # dest = os.path.join(upload_dir, random_file_name + file_extension)
    # with open(dest, "wb") as buffer:
    #    shutil.copyfileobj(file.file, buffer)

    return {"upload_url": f"{MEDIA_ROUTE}/" + random_file_name + file_extension}
