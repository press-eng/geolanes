from pydantic import BaseModel


class OtherContact(BaseModel):
    name: str
    contact_number: str
