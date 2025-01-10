from pydantic import BaseModel


class MediaResponse(BaseModel):
    upload_url: str
